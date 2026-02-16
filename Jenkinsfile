properties([
    pipelineTriggers([
        [
            $class: 'GenericTrigger',
            token: 'MY_PAYMENT_TOKEN',
            printContributedVariables: true,
            genericVariables: [
                [key: 'ref',       value: '$.ref'],
                [key: 'repo_name', value: '$.repository.name']
            ],
            regexpFilterText: '$repo_name:$ref',
            regexpFilterExpression: '^.+:refs/heads/.+$'
        ]
    ])
])

pipeline {
    agent any

    environment {
        // Git credentials
        GIT_CREDENTIALS = 'github-creds'

        // Nexus PyPI
        VENV                   = ".venv"
        NEXUS_PYPI_HOSTED      = "http://10.0.10.91:8081/repository/myapp-pypi-hosted/"
        NEXUS_PYPI_PROXY       = "http://10.0.10.91:8081/repository/myapp-pypi-proxy/simple"
        NEXUS_PYPI_CREDENTIALS = 'nexus-creds'

        // Nexus Docker Registry
        DOCKER_REPO            = 'myapp-docker-hosted'
        REGISTRY_HOSTNAME      = '3-98-125-121.sslip.io'
        REVERSE_PROXY_BASE_URL = 'https://3-98-125-121.sslip.io'
        APP_NAME               = 'checkout-payment-service'
        DOCKER_CREDENTIALS_ID  = 'docker-registry-creds'
    }

    stages {

        stage('Webhook Debug') {
            steps {
                echo "Branch: ${env.ref}"
                echo "Repo: ${env.repo_name}"
            }
        }

        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout') {
            steps {
                script {
                    env.branchName = env.ref.replace('refs/heads/', '')
                    echo "Checking out branch: ${env.branchName}"
                }

                git(
                    branch: env.branchName,
                    credentialsId: env.GIT_CREDENTIALS,
                    url: 'https://github.com/vincentino1/payment-service.git'
                )
            }
        }

stage('Set up Python') {
    steps {
        script {
            // Use credentials to access Nexus PyPI group
            withCredentials([usernamePassword(
                credentialsId: env.NEXUS_PYPI_CREDENTIALS,
                usernameVariable: 'NEXUS_USER',
                passwordVariable: 'NEXUS_PASS'
            )]) {
                sh """
                    python3 -m venv $VENV
                    . $VENV/bin/activate
                    pip install --upgrade pip
                    pip install --index-url http://$NEXUS_USER:$NEXUS_PASS@10.0.10.91:8081/repository/myapp-pypi-group/simple \\
                        --trusted-host 10.0.10.91 \\
                        -r requirements.txt
                """
            }
        }
    }
}


        stage('Run Tests') {
            steps {
                sh """
                    . $VENV/bin/activate
                    pytest tests/
                """
            }
        }

        stage('Publish to PyPI Hosted') {
            when {
                expression { env.branchName == 'main' }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.NEXUS_PYPI_CREDENTIALS,
                    usernameVariable: 'NEXUS_USERNAME',
                    passwordVariable: 'NEXUS_PASSWORD'
                )]) {
                    sh """
                        . $VENV/bin/activate
                        python -m build
                        twine upload \\
                            --repository-url $NEXUS_PYPI_HOSTED \\
                            -u $NEXUS_USERNAME \\
                            -p $NEXUS_PASSWORD \\
                            dist/*
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    env.IMAGE_NAME = "${REGISTRY_HOSTNAME}/${DOCKER_REPO}/${APP_NAME}:v${BUILD_NUMBER}"
                    docker.withRegistry(REVERSE_PROXY_BASE_URL, DOCKER_CREDENTIALS_ID) {
                        docker.build(env.IMAGE_NAME)
                    }
                    echo "Built image: ${env.IMAGE_NAME}"
                }
            }
        }

        stage('Push Docker Image to Nexus') {
            when {
                expression { env.branchName == 'main' }
            }
            steps {
                script {
                    docker.withRegistry(REVERSE_PROXY_BASE_URL, DOCKER_CREDENTIALS_ID) {
                        docker.image(env.IMAGE_NAME).push()
                    }
                    echo "Pushed Docker image: ${env.IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            script {
                if (env.IMAGE_NAME) {
                    sh "docker rmi ${env.IMAGE_NAME} || true"
                }
            }
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}

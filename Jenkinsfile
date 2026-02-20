properties([
    pipelineTriggers([
        [
            $class: 'GenericTrigger',
            token: 'MY_PAYMENT_TOKEN',
            printContributedVariables: true,
            genericVariables: [
                [key: 'ref', value: '$.ref'], 
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
        // Git
        GIT_CREDENTIALS = 'github-creds'
        GIT_BRANCH_URL  = 'https://github.com/vincentino1/payment-service.git'

        // Nexus Docker Registry
        DOCKER_REPO_PUSH      = 'myapp-docker-hosted'
        DOCKER_REPO_PULL      = 'myapp-docker-group'
        DOCKER_CREDENTIALS_ID = 'docker-registry-creds'

        APP_NAME = 'checkout-payment-service'

        // Nexus PyPI
        NEXUS_PYPI_CRED  = 'nexus-pypi-credentials'
        REGISTRY_DOMAIN  = 'repo.vinny-dev.com'
        PYPI_REPO_GROUP  = 'myapp-pypi-group'
        PYPI_REPO_HOSTED = 'myapp-pypi-hosted'

        // Python virtual environment
        VENV = ".venv"
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
                    if (!env.ref) {
                        error "Webhook did not send 'ref'. Cannot determine branch."
                    }

                    env.branchName = env.ref.replace('refs/heads/', '')
                    echo "Checking out branch: ${env.branchName}"
                }

                git(
                    branch: env.branchName,
                    credentialsId: env.GIT_CREDENTIALS,
                    url: env.GIT_BRANCH_URL
                )
            }
        }

        stage('Set up Python') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.NEXUS_PYPI_CRED,
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh '''
                        python3 -m venv ${VENV}
                        . ${VENV}/bin/activate
                        python3 -m pip install --upgrade pip
                        python3 -m pip install -r requirements.txt \
                            --index-url https://${NEXUS_USER}:${NEXUS_PASS}@${REGISTRY_DOMAIN}/repository/${PYPI_REPO_GROUP}/simple
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh """
                    . ${VENV}/bin/activate
                    pytest tests/
                """
            }
        }

        stage('Build & Upload to PyPI Nexus Registry') {
            when { expression { env.branchName == 'main' } }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.NEXUS_PYPI_CRED,
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh """
                        set -e
                        . ${VENV}/bin/activate

                        # Upgrade packaging tools
                        python3 -m pip install --upgrade pip wheel build twine

                        # Clean previous build artifacts
                        rm -rf dist/

                        # Build source and wheel distributions
                        python3 -m build --sdist --wheel .

                        # Upload to Nexus hosted PyPI repository
                        python3 -m twine upload \
                            --repository-url https://${NEXUS_USER}:${NEXUS_PASS}@${REGISTRY_DOMAIN}/repository/${PYPI_REPO_HOSTED}/ \
                            dist/* \
                            --skip-existing
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    env.IMAGE_NAME = "${env.NEXUS_URL}/${env.DOCKER_REPO_PUSH}/${env.APP_NAME}:v${env.BUILD_NUMBER}"

                    docker.withRegistry(
                        "https://${env.NEXUS_URL}",
                        env.DOCKER_CREDENTIALS_ID
                    ) {
                        docker.build(
                            env.IMAGE_NAME,
                            "--build-arg DOCKER_PRIVATE_REPO=${env.NEXUS_URL}/${env.DOCKER_REPO_PULL} ."
                        )
                    }

                    echo "Built Docker image: ${env.IMAGE_NAME}"
                }
            }
        }

        stage('Push Docker Image to Nexus') {
            when { expression { env.branchName == 'main' } }
            steps {
                script {
                    docker.withRegistry(
                        "https://${env.NEXUS_URL}",
                        env.DOCKER_CREDENTIALS_ID
                    ) {
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


// properties([
//     pipelineTriggers([
//         [
//             $class: 'GenericTrigger',
//             token: 'MY_PAYMENT_TOKEN',
//             printContributedVariables: true,
//             genericVariables: [
//                 [key: 'ref', value: '$.ref'],
//                 [key: 'repo_name', value: '$.repository.name']
//             ],
//             regexpFilterText: '$repo_name:$ref',
//             regexpFilterExpression: '^.+:refs/heads/.+$'
//         ]
//     ])
// ])

// pipeline {
//     agent any

//     environment {
//         // Git credentials
//         GIT_CREDENTIALS = 'github-creds'

//         // Nexus PyPI
//         VENV = ".venv"
//         NEXUS_PYPI_HOSTED = "http://10.0.10.91:8081/repository/myapp-pypi-hosted/"
//         NEXUS_PYPI_PROXY = "http://10.0.10.91:8081/repository/myapp-pypi-proxy/simple"
//         NEXUS_PYPI_CREDENTIALS = 'nexus-creds'

//         // Nexus Docker Registry
//         DOCKER_REPO = 'myapp-docker-hosted'
//         REGISTRY_HOSTNAME = '3-98-125-121.sslip.io'
//         REVERSE_PROXY_BASE_URL = 'https://3-98-125-121.sslip.io'
//         APP_NAME = 'checkout-payment-service'
//         DOCKER_CREDENTIALS_ID = 'docker-registry-creds'
//     }

//     stages {
//         stage('Webhook Debug') {
//             steps {
//                 echo "Branch: ${env.ref}"
//                 echo "Repo: ${env.repo_name}"
//             }
//         }

//         stage('Clean Workspace') {
//             steps {
//                 cleanWs()
//             }
//         }

//         stage('Checkout') {
//             steps {
//                 script {
//                     env.branchName = env.ref.replace('refs/heads/', '')
//                     echo "Checking out branch: ${env.branchName}"
//                 }
//                 git(
//                     branch: env.branchName,
//                     credentialsId: env.GIT_CREDENTIALS,
//                     url: 'https://github.com/vincentino1/payment-service.git'
//                 )
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     env.IMAGE_NAME = "${REGISTRY_HOSTNAME}/${DOCKER_REPO}/${APP_NAME}:v${BUILD_NUMBER}"
//                     docker.withRegistry(REVERSE_PROXY_BASE_URL, DOCKER_CREDENTIALS_ID) {
//                         docker.build(env.IMAGE_NAME)
//                     }
//                     echo "Built image: ${env.IMAGE_NAME}"
//                 }
//             }
//         }

//         stage('Push Docker Image to Nexus') {
//             when {
//                 expression { env.branchName == 'main' }
//             }
//             steps {
//                 script {
//                     docker.withRegistry(REVERSE_PROXY_BASE_URL, DOCKER_CREDENTIALS_ID) {
//                         docker.image(env.IMAGE_NAME).push()
//                     }
//                     echo "Pushed Docker image: ${env.IMAGE_NAME}"
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             script {
//                 if (env.IMAGE_NAME) {
//                     sh "docker rmi ${env.IMAGE_NAME} || true"
//                 }
//             }
//         }
//         success {
//             echo 'Pipeline completed successfully.'
//         }
//         failure {
//             echo 'Pipeline failed.'
//         }
//     }
// }

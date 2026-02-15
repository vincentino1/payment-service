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
            regexpFilterExpression: '^.+:refs/heads/.+$' // default to any repo_name and branch in the payload
        ]
    ])
])

pipeline {
    
    agent any       
    environment {
        // credentials for git
        GIT_CREDENTIALS = 'Git_Credential'

        NEXUS_PYPI_URL = "http://10-2-10-63.sslip.io/repository/myapp-pypi-group/simple" 
        NEXUS_PYPI_HOST = "10-2-10-63.sslip.io"
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
                echo "Deleting workspace..."
                cleanWs()   // or use deleteDir()
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
                    credentialsId: "${env.GIT_CREDENTIALS}",
                    url: 'https://github.com/vincentino1/payment-service.git'
                )
            }
        }

        stage('Set up Python') { // Install any dependencies you need to perform testing
            steps {
                sh '''
                    python3 -m venv .venv
                    . $VENV/bin/activate
                    --index-url $NEXUS_PYPI_URL \
                    --trusted-host $NEXUS_PYPI_HOST \
                    -r requirements.txt      
                    '''
              }
        }
        
        stage('Run Tests') { // Run pytest against your code
            steps {
                sh """
                    . $VENV/bin/activate
                    pytest tests/
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                    script {
                        env.IMAGE_NAME = "${REGISTRY_HOSTNAME}/${DOCKER_REPO}/${APP_Name}:v${BUILD_NUMBER}"

                        docker.withRegistry("${REVERSE_PROXY_BASE_URL}", "${DOCKER_CREDENTIALS_ID}") {
                            docker.build(env.IMAGE_NAME)
                        }

                        echo "Built image: ${env.IMAGE_NAME}"
            }
        }

        stage('Push Docker Image to Nexus') {
            when { 
                expression { return env.branchName == 'main'}
            }
            steps {
                script {
                    docker.withRegistry("${REVERSE_PROXY_BASE_URL}", "${DOCKER_CREDENTIALS_ID}") {
                        docker.image(env.IMAGE_NAME).push()
                    }

                    echo "Pushed Docker image: ${env.IMAGE_NAME}"

                }
            }
        }
    }

    post {
        always {
            sh 'docker rmi ${IMAGE_NAME} || true'  // Cleanup
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'The pipeline encountered an error and did not complete successfully.'
        }
    }
    
    
    }   

}

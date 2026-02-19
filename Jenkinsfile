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
        // Git credentials
        GIT_CREDENTIALS = 'github-creds'
        GIT_BRANCH_URL = 'https://github.com/vincentino1/payment-service.git'

        // Nexus Docker Registry
        DOCKER_REPO_PUSH = 'myapp-docker-hosted'
        DOCKER_REPO_PULL = 'myapp-docker-group'
        DOCKER_CREDENTIALS_ID = 'docker-registry-creds'

        APP_NAME = 'checkout-payment-service'

        // NEXUS_URL & DOCKER_REGISTRY_URL are set as Jenkins environment variables

        

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
                script {
                    // Install dependencies
                    sh """
                        python3 -m venv $VENV
                        . $VENV/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    """
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

        stage('Build Docker Image') {
            steps {
                script {
                    // Tag Docker image using BUILD_NUMBER only
                    env.IMAGE_NAME = "${env.DOCKER_REGISTRY_URL}/${env.DOCKER_REPO_PUSH}/${env.APP_NAME}:v${env.BUILD_NUMBER}"

                    docker.withRegistry("https://${env.DOCKER_REGISTRY_URL}", "${env.DOCKER_CREDENTIALS_ID}") {
                        docker.build(env.IMAGE_NAME, "--build-arg DOCKER_PRIVATE_REPO=${env.NEXUS_URL}/${env.DOCKER_REPO_PULL} .")
                    }

                    echo "Built Docker image: ${env.IMAGE_NAME}"
                }
            }
        }

        stage('Push Docker Image to Nexus') {
            when {
                expression { env.branchName == 'main' }
            }
            steps {
                script {
                    docker.withRegistry("https://${env.DOCKER_REGISTRY_URL}", "${env.DOCKER_CREDENTIALS_ID}") {
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

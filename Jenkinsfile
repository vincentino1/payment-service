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
        VENV_DIR     = ".venv"
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
                    python3 -m venv ${VENV_DIR}'
                    ./venv/bin/pip install -r requirements.txt         
                    '''
              }
        }
        
        stage('Run Tests') { // Run pytest against your code
            steps {
                sh './venv/bin/pytest tests/'        
            }
        }
    }   

}

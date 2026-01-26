properties([
    pipelineTriggers([
        [
            $class: 'GenericTrigger',
            token: 'MY_SPRING_TOKEN',
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

    tools {
        maven 'maven 3.6' // Name must match the one you configured in Jenkins
        jdk 'jdk17'
    }
        environment {
        // credentials for git
        GIT_CREDENTIALS = 'Git_Credential'
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
                    url: 'https://github.com/vincentino1/catalog-service.git'
                )
            }
        }

        stage('Install Dependencies') {
            steps {
                    sh 'mvn clean install -DskipTests'
            }
        }
    }
}

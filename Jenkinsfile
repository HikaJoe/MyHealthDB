pipeline {
    agent any

    environment {
        // Define environment variables for Docker Hub credentials
        DOCKER_CREDENTIALS_ID = 'Docker_Reg_Auth' // ID for Docker Hub credentials stored in Jenkins
    }

    stages {
        stage('Checkout') {
        steps {
            checkout scm: [$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/HikaJoe/MyHealthDB.git', credentialsId: 'GitHub']]]
        }
    }

        stage('Build Registration Image') {
            steps {
                // Build the Docker image from RegistrationDockerfile
                script {
                    def registrationImage = docker.build("yourusername/registration:${BUILD_NUMBER}", "-f RegistrationDockerfile .")
                }
            }
        }

        stage('Push Registration Image') {
            steps {
                // Log in and push the registration image to Docker Hub
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                        def registrationImage = docker.image("yourusername/registration:${BUILD_NUMBER}")
                        registrationImage.push()
                    }
                }
            }
        }

        stage('Build Login Image') {
            steps {
                // Build the Docker image from LoginDockerfile
                script {
                    def loginImage = docker.build("yourusername/login:${BUILD_NUMBER}", "-f LoginDockerfile .")
                }
            }
        }

        stage('Push Login Image') {
            steps {
                // Log in and push the login image to Docker Hub
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                        def loginImage = docker.image("yourusername/login:${BUILD_NUMBER}")
                        loginImage.push()
                    }
                }
            }
        }

        stage('Clean Up') {
            steps {
                // Optional: Clean up Docker images
                script {
                    docker.image("yourusername/registration:${BUILD_NUMBER}").remove()
                    docker.image("yourusername/login:${BUILD_NUMBER}").remove()
                }
            }
        }
    }

    post {
        always {
            // Always run steps, e.g., cleanup or notifications
            echo 'The pipeline has completed'
        }
    }
}

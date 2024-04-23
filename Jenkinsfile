pipeline {
    agent any

    environment {
        // Define environment variables
        DOCKER_IMAGE = 'yourusername/reponame:tag'
        DOCKER_CREDENTIALS_ID = 'Docker_Reg_Auth' // ID for Docker Hub credentials stored in Jenkins
    }

    stages {
        stage('Checkout') {
            steps {
                // Checks out the source code
                git 'https://github.com/HikaJoe/MyHealthDB.git'
            }
        }

        stage('Build') {
            steps {
                // Build the Docker image
                script {
                    docker.build(env.DOCKER_IMAGE)
                }
            }
        }

        stage('Push') {
            steps {
                // Log in and push the image to Docker Hub
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                        docker.image(env.DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('Clean Up') {
            steps {
                // Optional: Clean up Docker images
                script {
                    docker.image(env.DOCKER_IMAGE).remove()
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

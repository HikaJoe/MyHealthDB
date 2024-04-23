pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'Docker_Reg_Auth'
        LOGIN_IMAGE_TAG = "${GIT_COMMIT}"
        IMAGE_TAG_REG = 'Registration'
        IMAGE_TAG_LOG = 'Login'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        //build and push
        stage('Build and Push Images') {
            parallel {
                stage('Build and Push Registration Image') {
                    steps {
                        script {
                            def registrationImage = docker.build("hikajoe/myhealth:${IMAGE_TAG_REG}", "-f RegistrationDockerfile .")
                            docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                                registrationImage.push()
                            }
                        }
                    }
                }
                stage('Build and Push Login Image') {
                    steps {
                        script {
                            def loginImage = docker.build("hikajoe/myhealth:${IMAGE_TAG_LOG}", "-f LoginDockerfile .")
                            docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                                loginImage.push()
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up images
            script {
                sh '''
                    docker rmi hikajoe/myhealth:${IMAGE_TAG_REG}
                    docker rmi hikajoe/myhealth:${IMAGE_TAG_LOG}
                '''
            }
            echo 'The pipeline has completed'
        }
    }
}

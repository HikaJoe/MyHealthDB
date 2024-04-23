pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'Docker_Reg_Auth'
        REGISTRATION_IMAGE_TAG = "${GIT_COMMIT}"
        LOGIN_IMAGE_TAG = "${GIT_COMMIT}"
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
                            def registrationImage = docker.build("yourusername/myhealth:${REGISTRATION_IMAGE_TAG}", "-f RegistrationDockerfile .")
                            docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                                registrationImage.push()
                            }
                        }
                    }
                }
                stage('Build and Push Login Image') {
                    steps {
                        script {
                            def loginImage = docker.build("yourusername/myhealth:${LOGIN_IMAGE_TAG}", "-f LoginDockerfile .")
                            docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                                loginImage.push()
                            }
                        }
                    }
                }
            }
        }
        //deploy
        stage('Clean Up') {
            steps {
                script {
                    docker.image("yourusername/myhealth:${REGISTRATION_IMAGE_TAG}").remove()
                    docker.image("yourusername/myhealth:${LOGIN_IMAGE_TAG}").remove()
                }
            }
        }
    }

    post {
        always {
            echo 'The pipeline has completed'
        }
    }
}

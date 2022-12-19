pipeline {
  agent any
  stages {
    stage('version') {
      steps {
        sh 'python3 --version'
      }
    }
    stage('clone') {
      steps {
        git branch: 'master', credentialsId: 'Git', url: 'https://github.com/Sneha9191/hello.git'
      }
    }
    stage('hello') {
      steps {
        sh 'python3 hello.py'
      }
    }
  }
}

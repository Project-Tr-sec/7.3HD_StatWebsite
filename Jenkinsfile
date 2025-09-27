pipeline {
  agent any

  options { timestamps() }

  triggers {
    githubPush()          
    pollSCM('* * * * *')  
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python') {
      steps {
        bat '''
          python -m venv .venv
          call .venv\\Scripts\\activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Build') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          python -c "import os, flask; import app; print('cwd=', os.getcwd()); print('import app OK', app.__file__); print('Flask OK:', flask.__version__)"
        '''
      }
    }

    stage('Unit and Integration Tests') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          pytest
        '''
      }
    }

    stage('Code Analysis') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          black .
          isort . --profile black
          flake8 .
        '''
      }
    }

    stage('Security Scan') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          pip-audit -r requirements.txt --format cyclonedx --output sbom.json || echo "pip-audit found issues (non-fatal)"
          bandit -q -r . -f json -o bandit_report.json || echo "bandit found issues (non-fatal)"
          exit /b 0
        '''
      }
    }

    stage('Deploy to Staging') {
      steps { echo 'Pretend deploy to staging...' }
    }

    stage('Integration Tests on Staging') {
      steps { echo 'Pretend run integration tests on staging...' }
    }

  stage('Deploy to Staging') {
    steps {
      bat '''
        call .venv\\Scripts\\activate
        rem (optional) ensure deps are up-to-date on the host
        pip install -r requirements.txt

        rem restart the Windows service that runs waitress
        sc stop StatWebsite || echo "Service not running"
        sc start StatWebsite
      '''
    }
  }
}

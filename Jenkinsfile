pipeline {
  agent any

  options { timestamps() }

  triggers {
    githubPush()              
    pollSCM('H/5 * * * *')      
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
          python -c "import os, importlib.metadata as im; import app; print('cwd=', os.getcwd()); print('import app OK', app.__file__); print('Flask OK:', im.version('flask'))"
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
          rem Create reports but do not fail the pipeline
          pip-audit -r requirements.txt --format cyclonedx --output sbom.json || echo "pip-audit found issues (non-fatal)"
          bandit -q -r . -f json -o bandit_report.json || echo "bandit found issues (non-fatal)"
          exit /b 0
        '''
      }
    }

    stage('Deploy to Staging') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          rem Ensure deps are up to date for the service environment
          pip install -r requirements.txt

          rem Restart the Windows service that runs waitress (pre-created as 'StatWebsite')
          sc stop StatWebsite || echo "Service not running"
          sc start StatWebsite
        '''
      }
    }

    stage('Integration Tests on Staging') {
      steps {
        echo 'Pretend run integration tests on staging...'
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'bandit_report.json,sbom.json', allowEmptyArchive: true
    }
  }
}

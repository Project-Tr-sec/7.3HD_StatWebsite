pipeline {
  agent any
  options { timestamps(); timeout(time: 30, unit: 'MINUTES') }
  triggers { pollSCM('H/5 * * * *') }
  environment { VENV_PATH = '.venv' }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Setup Python') {
      steps {
        bat '''
          python -m venv "%VENV_PATH%"
          call "%VENV_PATH%\\Scripts\\activate"
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Build (import sanity)') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python - << "PY"
from app import create_app
app = create_app()
print("factory OK:", app.name)
PY
        '''
      }
    }

    stage('Unit Tests') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          pytest -q --junitxml=test-results.xml
        '''
      }
      post {
        always { junit 'test-results.xml'; archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true }
      }
    }

    stage('Style & Security (non-fatal)') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          black --check --diff . || echo black non-fatal
          isort --check-only --profile black . || echo isort non-fatal
          flake8 . || echo flake8 non-fatal
          pip-audit -r requirements.txt -f json -o pip_audit.json || echo pip-audit non-fatal
          bandit -q -r . -f json -o bandit_report.json || echo bandit non-fatal
        '''
      }
    }
  }

  post {
    always { archiveArtifacts artifacts: 'pip_audit.json,bandit_report.json', allowEmptyArchive: true; cleanWs() }
  }
}

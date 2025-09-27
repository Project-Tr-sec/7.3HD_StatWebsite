pipeline {
  agent any

  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  triggers {
    pollSCM('H/5 * * * *')
  }

  environment {
    VENV_DIR = '.venv'
    PY      = "${WORKSPACE}\\.venv\\Scripts\\python.exe"
    PIP     = "${WORKSPACE}\\.venv\\Scripts\\pip.exe"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python') {
      steps {
        bat """
          python -m venv "%VENV_DIR%"
          "%PY%" -m pip install --upgrade pip
          "%PIP%" install -r requirements.txt
        """
      }
    }

    stage('Build (import sanity)') {
      steps {
        powershell '''
          $py = "$PWD\\.venv\\Scripts\\python.exe"
          $code = @"
    import os
    import importlib.metadata as im
    from app import create_app

    app = create_app()
    print("cwd=", os.getcwd())
    print("app OK ->", app)
    print("Flask version:", im.version("flask"))
    "@
          $code | & $py -
        '''
      }
    }


    stage('Unit Tests') {
      steps {
        bat """
          "%PY%" -m pytest --junitxml=test-results.xml -v
        """
      }
      post {
        always {
          junit 'test-results.xml'
          archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
        }
      }
    }

    stage('Style & Security (non-fatal)') {
      steps {
        bat """
          "%PY%" -m black --check --diff .  || echo black non-fatal
          "%PY%" -m isort --check-only --profile black . || echo isort non-fatal
          "%PY%" -m flake8 . || echo flake8 non-fatal
          "%PY%" -m pip_audit -r requirements.txt -f json -o pip_audit.json || echo pip-audit non-fatal
          "%PY%" -m bandit -q -r . -f json -o bandit_report.json || echo bandit non-fatal
        """
      }
      post {
        always {
          archiveArtifacts artifacts: 'pip_audit.json,bandit_report.json', allowEmptyArchive: true
        }
      }
    }

    stage('Deploy to Vercel (optional)') {
      when {
        expression { env.BRANCH_NAME == 'main' }
      }
      steps {
        echo 'Skipping CLI deploy here. Let Vercel Git integration deploy on push to main.'
      }
    }
  }

  post {
    success { echo 'Pipeline finished ✅' }
    failure { echo 'Pipeline failed! Check logs.' }
  }
}

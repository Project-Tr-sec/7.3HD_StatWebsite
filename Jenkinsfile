pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    ansiColor('xterm')
  }

  triggers {
    pollSCM('H/1 * * * *')
  }

  environment {
    PY = 'python'         
    VENV = '.venv'
    STAGING_PORT = '5001'
    PROD_PORT = '5002'
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python') {
      steps {
        bat """
          %PY% -m venv %VENV%
          call %VENV%\\Scripts\\activate
          python -m pip install --upgrade pip
          if exist requirements.txt ( pip install -r requirements.txt ) else ( echo No requirements.txt found )
        """
      }
    }

    stage('Build') {
      steps {
        // For Python apps "build" usually just means "it installs and imports cleanly".
        bat """
          call %VENV%\\Scripts\\activate
          python -c "import sys; print('Python OK:', sys.version)"
          python -c "import flask; print('Flask OK:', flask.__version__)"
        """
      }
    }

    stage('Unit and Integration Tests') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          pip install pytest pytest-cov
          pytest -q --cov=app
        """
      }
      post {
        always {
          // If you later export JUnit XML, publish it here with `junit 'path/*.xml'`
          echo 'Tests completed.'
        }
      }
    }

    stage('Code Analysis') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          pip install black flake8 isort
          black --check .
          isort --check-only .
          flake8 .
        """
      }
    }

    stage('Security Scan') {
      steps {
        bat """
          call %VENV%\\Scripts\\activate
          pip install pip-audit bandit
          pip-audit
          bandit -r app -ll
        """
      }
    }

    stage('Deploy to Staging') {
      steps {
        bat """
          echo Stopping anything on port %STAGING_PORT% (if running)...
          for /f "tokens=5" %%p in ('netstat -ano ^| findstr :%STAGING_PORT% ^| findstr LISTENING') do taskkill /F /PID %%p 2>nul

          echo Starting StatCalc (staging) on port %STAGING_PORT%...
          call %VENV%\\Scripts\\activate
          set FLASK_APP=app:create_app
          start /B cmd /c "flask run --port=%STAGING_PORT% --host=0.0.0.0"

          echo Health check...
          curl -fsS http://localhost:%STAGING_PORT%/healthz
        """
      }
    }

    stage('Integration Tests on Staging') {
      steps {
        bat """
          echo Basic smoke tests against staging...
          curl -fsS http://localhost:%STAGING_PORT%/healthz
          REM add more curl tests for /api/calc if you want
        """
      }
    }

    stage('Deploy to Production') {
      when { buildingTag() }  // only run when building a Git tag (e.g., v1.0.0)
      steps {
        bat """
          echo Stopping anything on port %PROD_PORT% (if running)...
          for /f "tokens=5" %%p in ('netstat -ano ^| findstr :%PROD_PORT% ^| findstr LISTENING') do taskkill /F /PID %%p 2>nul

          echo Starting StatCalc (prod) on port %PROD_PORT%...
          call %VENV%\\Scripts\\activate
          set FLASK_APP=app:create_app
          start /B cmd /c "flask run --port=%PROD_PORT% --host=0.0.0.0"

          echo Prod health check...
          curl -fsS http://localhost:%PROD_PORT%/healthz
        """
      }
    }
  }

  post {
    success {
      echo 'Pipeline finished successfully '
    }
    failure {
      echo 'Pipeline failed  — check logs above.'
    }
  }
}

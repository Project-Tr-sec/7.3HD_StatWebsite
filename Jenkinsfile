pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  triggers {

    pollSCM('* * * * *')
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
                bat """
                call .venv\\Scripts\\activate
                set PYTHONPATH=%CD%
                python -c "import sys, os; print('cwd=', os.getcwd()); import app; print('import app OK', app.__file__)"
                python -c "import flask, importlib.metadata as im; print('Flask OK:', im.version('flask'))"
                """
            }
    }

        stage('Unit and Integration Tests') {
            steps {
                bat '''
                    call .venv\\Scripts\\activate
                    set PYTHONPATH=%CD%
                    python -m pytest tests/ -v
                '''
            }
    }

        stage('Code Analysis') {
            steps {
                bat """
                call .venv\\Scripts\\activate
                black .
                isort . --profile black
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
          curl -fsS http://localhost:%STAGING_PORT%/healthz
        """
      }
    }

    stage('Deploy to Production') {
      when { buildingTag() }
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
}
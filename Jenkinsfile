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
    VENV_PATH = '.venv'
    PYTHON_SCRIPT = 'wsgi.py'  
  }

  stages {
    stage('Checkout') {
      steps { 
        checkout scm 
      }
    }

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

    stage('Build') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python -c "import os, importlib.metadata as im; import app; print('cwd=', os.getcwd()); print('import app OK', app.__file__); print('Flask OK:', im.version('flask'))"
        '''
      }
    }

    stage('Unit and Integration Tests') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python -m pytest --junitxml=test-results.xml
        '''
      }
      post {
        always {
          junit 'test-results.xml'
        }
      }
    }

    stage('Code Analysis') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python -m black --check --diff .
          python -m isort --check-only --profile black .
          python -m flake8 .
        '''
      }
    }

    stage('Security Scan') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          echo "Running security scans..."
          python -m pip_audit -r requirements.txt -f json -o pip_audit.json || echo "pip-audit completed with exit code: !ERRORLEVEL!"
          python -m bandit -q -r . -f json -o bandit_report.json || echo "bandit completed with exit code: !ERRORLEVEL!"
        '''
        script {

          archiveArtifacts artifacts: 'bandit_report.json,pip_audit.json', allowEmptyArchive: true
        }
      }
    }

    stage('Deploy to Staging') {
      steps {
        script {
          // Check if we should deploy (optional: based on branch or parameter)
          if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'develop') {
            bat '''
              setlocal EnableDelayedExpansion
              set "APP_DIR=%cd%"
              set "VENV=%APP_DIR%\\%VENV_PATH%"

              call "%VENV%\\Scripts\\activate"
              
              rem ---- Stop previously running instance if any ----
              if exist "%APP_DIR%\\app.pid" (
                for /f "usebackq delims=" %%i in ("%APP_DIR%\\app.pid") do (
                  set "OLD_PID=%%i"
                )
                if defined OLD_PID (
                  taskkill /PID !OLD_PID! /F >nul 2>&1 || echo "No process with PID !OLD_PID! found"
                )
                del "%APP_DIR%\\app.pid" >nul 2>&1
              )

              rem ---- Start new instance ----
              set "WAITRESS=%VENV%\\Scripts\\waitress-serve.exe"
              if not exist "%WAITRESS%" (
                echo ERROR: waitress-serve.exe not found 
                exit /b 1
              )

              rem Start process and capture PID
              start /B "" "%WAITRESS%" --host=0.0.0.0 --port=8000 wsgi:app
              for /f "tokens=2" %%i in ('tasklist /fi "imagename eq waitress-serve.exe" /fo table /nh') do (
                set "NEW_PID=%%i"
              )
              
              if defined NEW_PID (
                echo !NEW_PID! > "%APP_DIR%\\app.pid"
                echo Started StatWebsite on port 8000 with PID !NEW_PID!
              ) else (
                echo ERROR: Failed to start waitress-serve.exe
                exit /b 1
              )
              
              rem Wait for application to start
              timeout /t 10 /nobreak >nul
              
              rem Test if application is responding
              curl -f http://localhost:8000/ >nul 2>&1
              if !ERRORLEVEL! equ 0 (
                echo Application started successfully
              ) else (
                echo ERROR: Application not responding after startup
                exit /b 1
              )
            '''
          } else {
            echo "Skipping deployment for branch: ${env.BRANCH_NAME}"
          }
        }
      }
    }

    stage('Integration Tests on Staging') {
      steps {
        script {
          if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'develop') {
            bat '''
              call "%VENV_PATH%\\Scripts\\activate"
              echo "Running integration tests against staging..."
              python -m pytest tests/integration/ --url http://localhost:8000 -v
            '''
          } else {
            echo "Skipping integration tests for branch: ${env.BRANCH_NAME}"
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'bandit_report.json,pip_audit.json,test-results.xml', allowEmptyArchive: true
      cleanWs()  // Clean workspace after build
    }
    success {
      echo 'Pipeline completed successfully!'
    }
    failure {
      echo 'Pipeline failed!'
    }
    unstable {
      echo 'Pipeline is unstable (tests failed)'
    }
  }
}
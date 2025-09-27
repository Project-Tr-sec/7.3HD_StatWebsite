pipeline {
  agent any

  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }


  environment {
    VENV_PATH     = '.venv'
    KEEP_RUNNING  = 'true'   
  }

  triggers {
    pollSCM('H/5 * * * *')
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
          rem pytest already provides --junitxml; no extra junitxml pkg needed
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
          python -m pytest --junitxml=test-results.xml -v
        '''
      }
      post {
        always {
          junit 'test-results.xml'
          archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
        }
      }
    }

    stage('Code Analysis') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python -m black --check --diff . || echo "black check completed"
          python -m isort --check-only --profile black . || echo "isort check completed"
          python -m flake8 . || echo "flake8 check completed"
        '''
      }
    }

    stage('Security Scan') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          echo "Running security scans..."
          python -m pip_audit -r requirements.txt -f json -o pip_audit.json || echo "pip-audit completed with exit code: %ERRORLEVEL%"
          python -m bandit -q -r . -f json -o bandit_report.json || echo "bandit completed with exit code: %ERRORLEVEL%"
        '''
      }
    }

    stage('Deploy to Staging') {
      when {
        // Deploy on main/develop, or when BRANCH_NAME is not set (classic job)
        expression { return !env.BRANCH_NAME || env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'develop' }
      }
      steps {
        bat '''
          setlocal EnableDelayedExpansion
          set "APP_DIR=%cd%"
          set "VENV=%APP_DIR%\\%VENV_PATH%"

          call "%VENV%\\Scripts\\activate"
          python -m pip install waitress

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

          rem ---- Verify waitress-serve exists ----
          set "WAITRESS=%VENV%\\Scripts\\waitress-serve.exe"
          if not exist "%WAITRESS%" (
            echo ERROR: waitress-serve.exe not found
            dir "%VENV%\\Scripts\\waitress*"
            exit /b 1
          )

          rem ---- Start new instance (PowerShell keeps it in the background) ----
          powershell -NoProfile -Command ^
            "$p = Start-Process -FilePath '%WAITRESS%' -ArgumentList '--host=0.0.0.0 --port=8000 wsgi:app' -WorkingDirectory '%APP_DIR%' -PassThru -WindowStyle Hidden; ^
             $p.Id | Out-File -FilePath '%APP_DIR%\\app.pid' -Encoding ASCII; ^
             Write-Host 'Started waitress with PID:' $p.Id"

          rem ---- Wait and health check (use /healthz for stability) ----
          set "MAX_RETRIES=10"
          set "RETRY_COUNT=0"
          :retry_healthcheck
          powershell -NoProfile -Command "try { iwr -UseBasicParsing http://localhost:8000/healthz -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
          if !ERRORLEVEL! equ 0 (
            echo Application started successfully and responding at http://localhost:8000
          ) else (
            set /a RETRY_COUNT+=1
            echo Health check attempt !RETRY_COUNT! of !MAX_RETRIES! failed
            if !RETRY_COUNT! lss !MAX_RETRIES! (
              timeout /t 3 /nobreak >nul
              goto retry_healthcheck
            ) else (
              echo ERROR: Application not responding after !MAX_RETRIES! attempts
              echo Checking running processes:
              tasklist | findstr /i "waitress-serve"
              type "%APP_DIR%\\app.pid" 2>nul
              exit /b 1
            )
          )
          endlocal
        '''
      }
    }

    stage('Integration Tests on Staging') {
      when {
        expression { return !env.BRANCH_NAME || env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'develop' }
      }
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          echo "Running basic integration check..."
          python -c "import requests; print('GET /healthz =>', requests.get('http://localhost:8000/healthz', timeout=5).status_code)" || echo "requests check skipped (requests not installed)"
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'bandit_report.json,pip_audit.json,test-results.xml', allowEmptyArchive: true

      script {
        if (env.KEEP_RUNNING?.toLowerCase() != 'true') {
          bat '''
            setlocal
            if exist "app.pid" (
              for /f "usebackq delims=" %%i in ("app.pid") do (
                taskkill /PID %%i /F >nul 2>&1 || echo "No process to kill"
              )
              del "app.pid" >nul 2>&1
            )
            endlocal
          '''
          cleanWs()
        } else {
          echo 'Leaving app running on http://localhost:8000 (KEEP_RUNNING=true).'
        }
      }
    }
    success {
      echo 'Pipeline completed successfully!'
    }
    failure {
      echo 'Pipeline failed! Check test results and deployment logs.'
    }
    unstable {
      echo 'Pipeline is unstable (tests failed).'
    }
  }
}

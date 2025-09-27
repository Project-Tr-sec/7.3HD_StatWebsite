pipeline {
  agent any

  options { timestamps() }

  triggers {
    githubPush()               // build on GitHub push (requires webhook)
    pollSCM('H/5 * * * *')     // safe hashed 5-min polling as fallback
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
          rem Use JSON output; cyclonedx not supported in this pip-audit build
          pip-audit -r requirements.txt -f json -o pip_audit.json || echo "pip-audit found issues (non-fatal)"
          bandit -q -r . -f json -o bandit_report.json || echo "bandit found issues (non-fatal)"
          exit /b 0
        '''
      }
    }

    stage('Deploy to Staging') {
      steps {
        bat '''
          setlocal
          set "APP_DIR=%cd%"
          set "VENV=%APP_DIR%\\.venv"

          call "%VENV%\\Scripts\\activate"
          pip install -r requirements.txt
          pip install waitress

          rem ---- Stop previously running instance if any (uses app.pid) ----
          powershell -NoProfile -ExecutionPolicy Bypass ^
            "if (Test-Path '%APP_DIR%\\app.pid') {" ^
            "  try { $pid = Get-Content '%APP_DIR%\\app.pid'; if ($pid) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } } catch {} ;" ^
            "  Remove-Item '%APP_DIR%\\app.pid' -ErrorAction SilentlyContinue" ^
            "}"

          rem ---- Start new instance in background via PowerShell, capture PID ----
          set "WAITRESS=%VENV%\\Scripts\\waitress-serve.exe"
          if not exist "%WAITRESS%" (
            echo ERROR: waitress-serve.exe not found && exit /b 1
          )

          powershell -NoProfile -ExecutionPolicy Bypass ^
            "$exe = '%WAITRESS%';" ^
            "$args = '--host=0.0.0.0 --port=8000 wsgi:app';" ^
            "$p = Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory '%APP_DIR%' -PassThru;" ^
            "$p.Id | Out-File -FilePath '%APP_DIR%\\app.pid' -Encoding ascii;" ^
            "Write-Host ('Started StatWebsite on port 8000 with PID ' + $p.Id)"

          endlocal
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
      archiveArtifacts artifacts: 'bandit_report.json,pip_audit.json', allowEmptyArchive: true
    }
  }
}

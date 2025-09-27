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
          set APP_DIR=%cd%
          set VENV=%APP_DIR%\\.venv

          call "%VENV%\\Scripts\\activate"
          pip install -r requirements.txt
          pip install waitress

          rem If service missing, install it with NSSM (nssm.exe must be on PATH)
          sc query StatWebsite >NUL 2>&1
          if %errorlevel% EQU 1060 (
            echo Service StatWebsite not found. Installing with NSSM...
            where nssm || (echo ERROR: nssm.exe not found on PATH & exit /b 1)
            nssm install StatWebsite "%VENV%\\Scripts\\waitress-serve.exe" --host=0.0.0.0 --port=8000 wsgi:app
            nssm set StatWebsite AppDirectory "%APP_DIR%"
            nssm set StatWebsite Start SERVICE_AUTO_START
          )

          rem Restart (ignore stop failure if not running)
          sc stop StatWebsite || echo "Service not running"
          sc start StatWebsite
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

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
    // OPTIONAL: add a Deploy Hook URL in Jenkins (Manage Jenkins → Credentials or as an env)
    // VERCEL_DEPLOY_HOOK = credentials('vercel-deploy-hook') // or plain env var
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
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

    stage('Build (import sanity)') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          python - <<PY
import os, importlib.metadata as im
from app import create_app
app = create_app()
print("cwd=", os.getcwd())
print("Flask OK:", im.version("flask"))
PY
        '''
      }
    }

    stage('Unit Tests') {
      steps {
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          pytest -q --junitxml=test-results.xml -v
        '''
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
        bat '''
          call "%VENV_PATH%\\Scripts\\activate"
          echo ==== BLACK ====
          python -m black --check --diff . || echo black non-fatal
          echo ==== ISORT ====
          python -m isort --check-only --profile black . || echo isort non-fatal
          echo ==== FLAKE8 ====
          python -m flake8 . || echo flake8 non-fatal
          echo ==== pip-audit ====
          python -m pip_audit -r requirements.txt -f json -o pip_audit.json || echo pip-audit non-fatal
          echo ==== bandit ====
          python -m bandit -q -r . -f json -o bandit_report.json || echo bandit non-fatal
        '''
      }
      post {
        always {
          archiveArtifacts artifacts: 'bandit_report.json,pip_audit.json', allowEmptyArchive: true
        }
      }
    }

    // OPTIONAL: only if you want Jenkins to ping Vercel (recommended path is GitHub → Vercel auto-deploy)
    stage('Deploy to Vercel (optional)') {
      when {
        allOf {
          expression { return env.VERCEL_DEPLOY_HOOK && env.VERCEL_DEPLOY_HOOK.trim() != '' }
          anyOf {
            branch 'main'
            branch 'develop'
          }
        }
      }
      steps {
        echo "Triggering Vercel deploy via deploy hook"
        powershell """
          try {
            Invoke-RestMethod -Method POST -Uri "$env:VERCEL_DEPLOY_HOOK" | Out-Host
          } catch {
            Write-Host 'Vercel hook failed:' $_.Exception.Message
            exit 1
          }
        """
      }
    }
  }

  post {
    success { echo 'Pipeline completed successfully!' }
    failure { echo 'Pipeline failed! Check logs.' }
    unstable { echo 'Pipeline unstable.' }
  }
}

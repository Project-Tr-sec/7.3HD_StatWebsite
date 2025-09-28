pipeline {
  agent any

  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  triggers {
    pollSCM('* * * * *')
  }

  environment {
    VENV_DIR = '.venv'
    PY       = "${WORKSPACE}\\.venv\\Scripts\\python.exe"
    PIP      = "${WORKSPACE}\\.venv\\Scripts\\pip.exe"

    // Use safer credential handling
    SONAR_HOST_URL = credentials('sonar-host-url') { optional: true }
    SONAR_TOKEN    = credentials('sonar-token') { optional: true }
    VERCEL_TOKEN   = credentials('vercel-token') { optional: true }
    GH_TOKEN       = credentials('github-token') { optional: true }
    MONITOR_URL    = ''
    APP_NAME       = 'statwebsite'
    // Fix environment variable reference
    BUILD_ARTIFACT = "build\\${APP_NAME}-${BUILD_NUMBER}.zip"
    DOCKER_IMAGE   = "ghcr.io/your-org/${APP_NAME}:${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        bat 'if not exist build mkdir build'
      }
    }

    stage('Setup Python') {
      steps {
        bat """
          python -m venv "%VENV_DIR%"
          "%PY%" -m pip install --upgrade pip wheel setuptools
          if exist requirements.txt ("%PIP%" install -r requirements.txt) else (echo No requirements.txt found)
        """
      }
    }

    stage('Build (artefact)') {
      steps {
        powershell '''
          $py = "$PWD\\.venv\\Scripts\\python.exe"
          $code = @"
import os
print('cwd=', os.getcwd())
try:
    from app import create_app
    app = create_app()
    print('app OK ->', app)
except Exception as e:
    raise SystemExit(f'Import failed: {e}')
"@
          $code | & $py -
        '''

        powershell '''
          if (!(Test-Path build)) { New-Item -ItemType Directory -Path build | Out-Null }
          $dest = "build\\statwebsite-${env:BUILD_NUMBER}.zip"
          if (Test-Path $dest) { Remove-Item $dest -Force }
          $items = Get-ChildItem -Force | Where-Object {
            $_.Name -notin @('.venv','.git','build') -and $_.Name -ne '.gitignore'
          }
          Compress-Archive -Path $items -DestinationPath $dest -CompressionLevel Optimal
        '''
        archiveArtifacts artifacts: 'build/*.zip', fingerprint: true
      }
    }

    stage('Unit Tests') {
      steps {
        bat """
          "%PY%" -m pip install pytest
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

    stage('Code Quality') {
      steps {
        bat """
          "%PY%" -m pip install black isort flake8
          "%PY%" -m black --check --diff .  || echo black non-fatal
          "%PY%" -m isort --check-only --profile black . || echo isort non-fatal
          "%PY%" -m flake8 . || echo flake8 non-fatal
        """
        script {
          // Safer credential checking
          if (env.SONAR_HOST_URL && env.SONAR_HOST_URL != 'sonar-host-url' && env.SONAR_TOKEN && env.SONAR_TOKEN != 'sonar-token') {
            bat """
              sonar-scanner ^
                -Dsonar.host.url=%SONAR_HOST_URL% ^
                -Dsonar.login=%SONAR_TOKEN% ^
                -Dsonar.projectKey=${APP_NAME} ^
                -Dsonar.projectBaseDir=%WORKSPACE% ^
                -Dsonar.sources=.
            """
          } else {
            echo 'Sonar not configured; skipped.'
          }
        }
      }
    }

    stage('Security') {
      steps {
        bat """
          "%PY%" -m pip install pip-audit bandit
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

    stage('Deploy (Staging)') {
      when { anyOf { branch 'main'; branch 'master'; branch 'staging' } }
      steps {
        script {
          // Safer credential checking
          if (env.VERCEL_TOKEN && env.VERCEL_TOKEN != 'vercel-token') {
            bat """
              vercel pull --yes --environment=production --token %VERCEL_TOKEN% || echo vercel pull skipped
              vercel deploy --prebuilt --token %VERCEL_TOKEN% || echo vercel deploy skipped
            """
          } else {
            echo 'No VERCEL_TOKEN; using artefact publish as staging deliverable.'
          }
        }
      }
    }

    stage('Release (Promotion)') {
      when { branch 'main' }
      steps {
        bat """
          git config user.email "ci@jenkins"
          git config user.name "Jenkins CI"
          git tag -a "v${BUILD_NUMBER}" -m "CI release ${BUILD_NUMBER}" || echo tag exists
          git push origin "v${BUILD_NUMBER}" || echo push tag skipped
        """
        script {
          // Safer credential checking
          if (env.GH_TOKEN && env.GH_TOKEN != 'github-token') {
            def body = "{\"tag_name\":\"v${BUILD_NUMBER}\",\"name\":\"Release ${BUILD_NUMBER}\",\"body\":\"Automated release by Jenkins\",\"draft\":false,\"prerelease\":false}"
            bat """
              curl -s -H "Authorization: token %GH_TOKEN%" ^
                   -H "Accept: application/vnd.github+json" ^
                   --data "${body}" ^
                   https://api.github.com/repos/your-org/${APP_NAME}/releases || echo GH release skipped
            """
          } else {
            echo 'No GH_TOKEN; created git tag only.'
          }
        }
      }
    }

    stage('Monitoring & Alerting (Smoke)') {
      steps {
        script {
          if (env.MONITOR_URL?.trim()) {
            powershell '''
              try {
                $resp = Invoke-WebRequest -UseBasicParsing "$env:MONITOR_URL"
                if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) {
                  $healthStatus = @{
                    status = $resp.StatusCode
                    time = Get-Date
                  }
                  $healthStatus | ConvertTo-Json | Set-Content -Path health.json
                } else {
                  Write-Error "Health NOT OK: $($resp.StatusCode)"
                  exit 1
                }
              } catch {
                Write-Error $_
                exit 1
              }
            '''
          } else {
            writeFile file: 'health.json', text: '{"status":"skipped","reason":"MONITOR_URL not set"}'
          }
        }
      }
      post {
        always {
          archiveArtifacts artifacts: 'health.json', allowEmptyArchive: true
        }
      }
    }
  }

  post {
    success { echo 'Pipeline finished' }
    failure { echo 'Pipeline failed — check the stage logs above.' }
    always  { 
      script {
        def artifactPath = "build\\${APP_NAME}-${BUILD_NUMBER}.zip"
        echo "Build artefact (if created): ${artifactPath}"
      }
    }
  }
}
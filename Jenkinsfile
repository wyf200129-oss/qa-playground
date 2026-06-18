pipeline {
    agent any

    environment {
        CI                 = 'true'
        ALLURE_RESULTS_DIR = 'allure-results'
        ALLURE_REPORT_DIR  = 'allure-report'
    }

    stages {

        // ── 1. 环境检查 ────────────────────────────
        stage('Env Check') {
            steps {
                echo '🔍 检查 Python 环境...'
                bat 'python --version && echo Python OK'
            }
        }

        // ── 2. 安装依赖 ──────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '📦 安装 POM 框架依赖...'
                dir('automation-demos/ui-pom') {
                    bat '''
                        python -m venv .venv
                        call .venv/Scripts/activate.bat
                        pip install -r requirements.txt
                        pip install allure-pytest
                    '''
                }
            }
        }

        // ── 3. 运行测试 ──────────────────────────────
        stage('Run POM Tests') {
            steps {
                echo '🧪 执行 Mock CI 演示测试（全流程 Mock，不依赖 ERP 后端）...'
                dir('automation-demos/ui-pom') {
                    bat '''
                        call .venv/Scripts/activate.bat
                        python -m pytest test_cases/test_mock_ci.py -v --tb=short --alluredir=%ALLURE_RESULTS_DIR% -p no:warnings
                    '''
                }
            }
            post {
                always {
                    echo '📊 测试执行完毕'
                }
            }
        }

        // ── 4. 生成 Allure 报告 ─────────────────────
        stage('Allure Report') {
            steps {
                echo '📈 生成 Allure 测试报告...'
                bat 'allure generate %ALLURE_RESULTS_DIR% --clean -o %ALLURE_REPORT_DIR%'
                allure includeProperties: false,
                       jdk: '',
                       report: 'allure-report',
                       results: [[path: 'allure-results']]
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline 执行成功！'
        }
        failure {
            echo '❌ Pipeline 执行失败，请检查测试日志。'
        }
        always {
            cleanWs()
        }
    }
}

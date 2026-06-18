pipeline {
    agent any

    environment {
        CI                 = 'true'
        ALLURE_RESULTS_DIR = 'allure-results'
        ALLURE_REPORT_DIR  = 'allure-report'
    }

    stages {

        // ── 1. 拉取代码 + 环境检查 ──────────────────
        stage('Checkout') {
            steps {
                echo '📥 拉取 qa-playground 仓库代码...'
                checkout scm

                echo '🔍 检查 Python 环境...'
                bat 'python --version'

                echo '🔍 检查 Chrome...'
                bat 'where chrome 2>nul || echo Chrome not in PATH (webdriver-manager will auto-download)'
            }
        }

        // ── 2. 安装依赖 ──────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '📦 安装 POM 框架依赖...'
                dir('automation-demos/ui-pom') {
                    bat '''
                        python -m venv .venv
                        call .venv\\Scripts\\activate.bat
                        pip install -r requirements.txt
                        pip install allure-pytest
                    '''
                }
            }
        }

        // ── 3. 运行测试 ──────────────────────────────
        stage('Run POM Tests') {
            steps {
                echo '🧪 执行 ERP 供应商模块 UI 测试...'
                dir('automation-demos/ui-pom') {
                    bat '''
                        call .venv\\Scripts\\activate.bat
                        python -m pytest test_cases/ -v --tb=short --alluredir=%ALLURE_RESULTS_DIR% -p no:warnings
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

pipeline {
    agent any

    environment {
        CI = 'true'
    }

    stages {

        // ── 1. 拉取代码 + 环境检查 ──────────────────
        stage('Checkout') {
            steps {
                echo '📥 拉取 qa-playground 仓库代码...'
                checkout scm

                echo '🔍 检查 Python 环境...'
                bat 'python --version'
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
                        pip install -r requirements.txt --proxy http://127.0.0.1:7897
                        pip install allure-pytest --proxy http://127.0.0.1:7897
                    '''
                }
            }
        }

        // ── 3. 运行测试（测试失败不阻断流水线）─────
        stage('Run POM Tests') {
            steps {
                echo '🧪 执行 ERP 供应商模块 UI 测试...'
                dir('automation-demos/ui-pom') {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        bat '''
                            call .venv\\Scripts\\activate.bat
                            python -m pytest test_cases/ -v --tb=short --alluredir=allure-results -p no:warnings
                        '''
                    }
                }
            }
            post {
                always {
                    echo '📊 测试执行完毕'
                }
            }
        }

        // ── 4. 生成 Allure 报告（CLI 未装时跳过）────
        stage('Allure Report') {
            steps {
                echo '📈 生成 Allure 测试报告...'
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    dir('automation-demos/ui-pom') {
                        bat 'allure generate allure-results --clean -o allure-report'
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline 执行成功！'
        }
        unstable {
            echo '⚠️ Pipeline 完成（部分测试未通过或工具缺失，属正常现象）'
        }
        failure {
            echo '❌ Pipeline 执行失败，请检查测试日志。'
        }
        always {
            cleanWs()
        }
    }
}

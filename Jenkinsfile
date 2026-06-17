pipeline {
    agent any

    environment {
        // Chrome 无头模式（CI 环境必须）
        CI                     = 'true'
        // Allure 报告输出目录
        ALLURE_RESULTS_DIR     = 'allure-results'
        ALLURE_REPORT_DIR      = 'allure-report'
    }

    stages {

        // ── 1. 拉取代码 ──────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 拉取 qa-playground 仓库代码...'
                checkout scm
                sh 'python --version && pip --version'
                sh 'google-chrome --version'
            }
        }

        // ── 2. 安装依赖 ──────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '📦 安装 POM 框架依赖...'
                dir('automation-demos/ui-pom') {
                    sh '''#!/bin/bash
                        python -m venv .venv
                        source .venv/bin/activate
                        pip install -r requirements.txt
                        pip install allure-pytest
                    '''
                }
            }
        }

        // ── 3. 运行自动化测试 ──────────────────────
        stage('Run POM Tests') {
            steps {
                echo '🧪 执行 ERP 供应商模块 UI 测试...'
                dir('automation-demos/ui-pom') {
                    sh '''#!/bin/bash
                        source .venv/bin/activate
                        python -m pytest test_cases/ \
                            -v \
                            --tb=short \
                            --alluredir=$WORKSPACE/$ALLURE_RESULTS_DIR \
                            -p no:warnings
                    '''
                }
            }
            post {
                always {
                    echo '📊 测试执行完毕，收集结果...'
                }
            }
        }

        // ── 4. 生成 Allure 报告 ─────────────────────
        stage('Allure Report') {
            steps {
                echo '📈 生成 Allure 测试报告...'
                sh '''
                    allure generate $ALLURE_RESULTS_DIR \
                        --clean \
                        -o $ALLURE_REPORT_DIR
                '''
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

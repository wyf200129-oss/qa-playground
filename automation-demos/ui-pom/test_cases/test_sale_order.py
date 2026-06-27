import allure
import pytest

from conf.yaml_conf import read


@allure.epic('销售管理')
@allure.feature('销售订单')
@allure.story('新增销售订单')
@allure.title('新增销售订单并查询验证')
@allure.description('基于 POM 页面对象与 YAML 业务数据实现销售订单新增、保存与查询')
@pytest.mark.parametrize('serve', ['TEST_ENV'], indirect=True)
@pytest.mark.parametrize('login', read('test_data/login.yaml'), indirect=True)
@pytest.mark.parametrize('data', read('test_data/sale_order.yaml'))
def test_add_sale_order(sale_order_page, serve, login, data):
    order_data = data['order']
    try:
        with allure.step('1. 新增销售订单'):
            sale_order_page.add_order(
                customer=order_data['customer'],
                goods_name=order_data['goods_name'],
                quantity=order_data['quantity'],
                price=order_data['price'],
                remark=order_data.get('remark', ''),
            )
        with allure.step('2. 保存订单'):
            order_no = sale_order_page.get_order_no()
            sale_order_page.save_order()
            sale_order_page.wait(data.get('wait', 3))
        with allure.step('3. 查询并断言订单已存在'):
            sale_order_page.search(order_no)
            sale_order_page.assert_text(
                order_no,
                'xpath',
                f'//td[contains(text(), "{order_no}")]',
            )
    except Exception:
        allure.attach(sale_order_page.get_png(), '报错截图', allure.attachment_type.PNG)
        raise

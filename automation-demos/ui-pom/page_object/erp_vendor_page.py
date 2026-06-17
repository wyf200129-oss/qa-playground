"""
ERP 系统 — 供应商管理页 Page Object

演示要点：
  1. Ant Design 弹窗的显式等待（不可见 = 保存成功并关闭）
  2. 完整的"新增 + 查询"业务闭环
"""

from base_page.basepage import BasePage


class ErpVendorPage(BasePage):
    """ERP 供应商管理页"""

    url = '[ERP_BASE_URL]/system/vendor'

    # ── 元素定位 ──────────────────────────────────
    vendor_add          = ('xpath', '//div[@class="table-operator"]/button[1]')
    supplier_name       = ('id', 'supplier')
    supplier_telephone  = ('id', 'telephone')
    supplier_save       = ('xpath', '//div[@class="ant-modal-footer"]/div[1]/button[2]')
    # 保存后的 Ant Design 弹窗（Modal）
    vendor_modal        = ('xpath', '//div[contains(@class, "ant-modal")]')

    search_name         = ('xpath', '//input[@placeholder="请输入名称查询"]')
    search_button       = ('xpath', '//span[text()="查 询"]/..')

    # ── 业务流程 ──────────────────────────────────

    def add_supplier(self, name: str, tele: str) -> None:
        """
        新增供应商，保存后等待弹窗关闭确认操作完成。

        步骤：
          1. 打开供应商管理页
          2. 点击「新增」按钮
          3. 填入供应商名称、电话
          4. 点击「保存」
          5. 显式等待弹窗关闭（替代 sleep(3)）
        """
        self.open(self.url)
        self.click(*self.vendor_add)
        self.input(*self.supplier_name, txt=name)
        self.input(*self.supplier_telephone, txt=tele)
        self.click(*self.supplier_save)

        # 显式等待：Ant Design Modal 关闭 → 保存操作完成
        self.wait_for_invisible(*self.vendor_modal, timeout=10)

    def search(self, name: str) -> None:
        """
        查询供应商。
        """
        self.open(self.url)
        self.input(*self.search_name, txt=name)
        self.click(*self.search_button)

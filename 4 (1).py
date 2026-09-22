import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os


class Resource:
    def __init__(self, res_id: int, name: str, res_category: str, res_type: str):
        self.res_id = res_id
        self.name = name
        self.res_category = res_category
        self.res_type = res_type


class ProductType:
    def __init__(self, type_id: int, name: str, cost: float):
        self.type_id = type_id
        self.name = name
        self.cost = cost


class Operation:
    def __init__(self, op_id: int, name: str, seq_num: int, duration_hours: int,
                 req_emp_type: str, req_machine_type: str = None):
        self.op_id = op_id
        self.name = name
        self.seq_num = seq_num
        self.duration_hours = duration_hours
        self.req_emp_type = req_emp_type
        self.req_machine_type = req_machine_type


class TechProcess:
    def __init__(self, tp_id: int, product_type_id: int, operations: list):
        self.tp_id = tp_id
        self.product_type_id = product_type_id
        self.operations = sorted(operations, key=lambda x: x.seq_num)


class Order:
    def __init__(self, order_id: int, product_type_id: int,
                 start_date: datetime.datetime, deadline: datetime.datetime):
        self.order_id = order_id
        self.product_type_id = product_type_id
        self.start_date = start_date
        self.deadline = deadline
        self.status = "Не запланирован"


class ScheduleElement:
    def __init__(self, order_id: int, op_name: str, emp_name: str, machine_name: str,
                 start_time: datetime.datetime, end_time: datetime.datetime):
        self.order_id = order_id
        self.op_name = op_name
        self.emp_name = emp_name
        self.machine_name = machine_name if machine_name else "Не требуется"
        self.start_time = start_time
        self.end_time = end_time


class DataManager:
    def __init__(self):
        self.resources = []
        self.product_types = []
        self.tech_processes = []
        self.orders = []
        self.schedule = []
        self._next_order_id = 100
        self.total_penalty = 0.0

    @staticmethod
    def _ensure_csv(filename, default_headers, default_rows):
        """Создаёт CSV-файл с заголовками и тестовыми данными, если он не существует."""
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(default_headers)
                writer.writerows(default_rows)

    def load_all_from_csv(self):
        """Загружает все данные из CSV-файлов, при отсутствии создаёт их с демо-данными."""
        # ----- resources.csv -----
        self._ensure_csv("resources.csv",
                         ["res_id", "name", "res_category", "res_type"],
                         [[1, "Иванов И.И.", "Сотрудник", "Токарь"],
                          [2, "Петров П.П.", "Сотрудник", "Сборщик"],
                          [3, "Сидоров С.С.", "Сотрудник", "Токарь"],
                          [4, "Станок Т-1", "Станок", "Токарный станок"],
                          [5, "Станок Т-2", "Станок", "Токарный станок"]])
        with open("resources.csv", encoding='utf-8') as f:
            for row in csv.DictReader(f):
                self.add_resource(Resource(int(row["res_id"]), row["name"],
                                           row["res_category"], row["res_type"]))

        # ----- product_types.csv -----
        self._ensure_csv("product_types.csv",
                         ["type_id", "name", "cost"],
                         [[1, "Деталь А", 5000.0],
                          [2, "Деталь Б", 8000.0]])
        with open("product_types.csv", encoding='utf-8') as f:
            for row in csv.DictReader(f):
                self.add_product_type(ProductType(int(row["type_id"]), row["name"],
                                                  float(row["cost"])))

        # ----- operations.csv -----
        self._ensure_csv("operations.csv",
                         ["op_id", "name", "seq_num", "duration_hours",
                          "req_emp_type", "req_machine_type"],
                         [[1, "Токарная обработка", 1, 4, "Токарь", "Токарный станок"],
                          [2, "Ручная сборка", 2, 3, "Сборщик", ""],
                          [3, "Токарная обработка", 1, 5, "Токарь", "Токарный станок"],
                          [4, "Контроль качества", 2, 2, "Сборщик", ""]])
        operations = []
        with open("operations.csv", encoding='utf-8') as f:
            for row in csv.DictReader(f):
                mach = row["req_machine_type"] if row["req_machine_type"] else None
                op = Operation(int(row["op_id"]), row["name"], int(row["seq_num"]),
                               int(row["duration_hours"]), row["req_emp_type"], mach)
                operations.append(op)
        self.operations = operations

        # ----- tech_processes.csv -----
        self._ensure_csv("tech_processes.csv",
                         ["tp_id", "product_type_id", "operation_ids"],
                         [[1, 1, "1|2"],
                          [2, 2, "3|4"]])
        with open("tech_processes.csv", encoding='utf-8') as f:
            for row in csv.DictReader(f):
                op_ids = list(map(int, row["operation_ids"].split("|")))
                ops = [o for o in self.operations if o.op_id in op_ids]
                self.add_tech_process(TechProcess(int(row["tp_id"]),
                                                  int(row["product_type_id"]), ops))

        # ----- orders.csv -----
        self._ensure_csv("orders.csv",
                         ["order_id", "product_type_id", "start_date", "deadline"],
                         [[101, 1, "2026-04-06 08:00", "2026-04-06 16:00"],
                          [102, 1, "2026-04-06 08:00", "2026-04-08 16:00"],
                          [103, 2, "2026-04-06 08:00", "2026-04-07 16:00"]])
        with open("orders.csv", encoding='utf-8') as f:
            for row in csv.DictReader(f):
                start = datetime.datetime.strptime(row["start_date"], "%Y-%m-%d %H:%M")
                deadline = datetime.datetime.strptime(row["deadline"], "%Y-%m-%d %H:%M")
                order = Order(int(row["order_id"]), int(row["product_type_id"]),
                              start, deadline)
                self.orders.append(order)
                if order.order_id >= self._next_order_id:
                    self._next_order_id = order.order_id + 1

    # --- CRUD операции ---
    def add_resource(self, res: Resource):
        self.resources.append(res)

    def add_product_type(self, pt: ProductType):
        self.product_types.append(pt)

    def add_tech_process(self, tp: TechProcess):
        self.tech_processes.append(tp)

    def add_order(self, product_type_id: int, start_date: datetime.datetime,
                  deadline: datetime.datetime) -> Order:
        self._next_order_id += 1
        new_order = Order(self._next_order_id, product_type_id, start_date, deadline)
        self.orders.append(new_order)
        return new_order

    def get_tech_process(self, product_type_id: int) -> TechProcess:
        for tp in self.tech_processes:
            if tp.product_type_id == product_type_id:
                return tp
        return None

    def find_resources(self, category: str, res_type: str) -> list:
        if not res_type:
            return [None]
        return [r for r in self.resources if r.res_category == category and r.res_type == res_type]


class Scheduler:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
        self.emp_busy = {}      # {emp_name: [(start, end), ...]}
        self.machine_busy = {}  # {machine_name: [(start, end), ...]}

    @staticmethod
    def _to_work_time(dt: datetime.datetime) -> datetime.datetime:
        """Приводит время к рабочему дню 8:00-16:00, пропуская выходные."""
        if dt.hour < 8:
            dt = dt.replace(hour=8, minute=0, second=0, microsecond=0)
        if dt.hour >= 16 or (dt.hour == 16 and dt.minute > 0):
            dt = dt + datetime.timedelta(days=1)
            dt = dt.replace(hour=8, minute=0, second=0, microsecond=0)
        # Пропуск субботы (5) и воскресенья (6)
        while dt.weekday() >= 5:
            dt = dt + datetime.timedelta(days=1)
            dt = dt.replace(hour=8, minute=0, second=0, microsecond=0)
        return dt

    @staticmethod
    def _find_slot(busy_intervals, desired_start: datetime.datetime, duration_hours: int):
        """
        busy_intervals: отсортированный список (start, end) занятых интервалов.
        Возвращает ближайшее время начала, когда операция длительностью duration_hours помещается.
        """
        candidate = desired_start
        for b_start, b_end in busy_intervals:
            if candidate + datetime.timedelta(hours=duration_hours) <= b_start:
                return candidate
            if candidate < b_end:
                candidate = b_end
        return candidate

    def _merge_intervals(self, intervals):
        """Сливает пересекающиеся интервалы для ускорения поиска."""
        if not intervals:
            return []
        intervals.sort()
        merged = [list(intervals[0])]
        for start, end in intervals[1:]:
            if start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return [(s, e) for s, e in merged]

    def schedule_orders(self):
        self.dm.schedule.clear()
        self.emp_busy.clear()
        self.machine_busy.clear()
        self.dm.total_penalty = 0.0

        # Сортируем заказы по дедлайну (срочные первыми)
        sorted_orders = sorted(self.dm.orders, key=lambda x: x.deadline)

        for order in sorted_orders:
            current_time = self._to_work_time(order.start_date)
            tp = self.dm.get_tech_process(order.product_type_id)
            if not tp:
                continue

            for op in tp.operations:
                emp_candidates = self.dm.find_resources("Сотрудник", op.req_emp_type)
                if not emp_candidates:
                    break  # нет сотрудника – заказ не планируется

                # Для станка – если не требуется, подставляем None
                mach_candidates = self.dm.find_resources("Станок", op.req_machine_type) or [None]

                best_start = None
                best_emp = None
                best_mach = None

                # Перебираем всех подходящих сотрудников и станки
                for emp in emp_candidates:
                    for mach in mach_candidates:
                        # Собираем интервалы занятости
                        busy = self.emp_busy.get(emp.name, []).copy()
                        if mach:
                            busy.extend(self.machine_busy.get(mach.name, []))
                        # Сортируем и сливаем интервалы для быстрого поиска
                        busy = self._merge_intervals(busy)
                        start = self._find_slot(busy, current_time, op.duration_hours)
                        start = self._to_work_time(start)

                        if best_start is None or start < best_start:
                            best_start = start
                            best_emp = emp
                            best_mach = mach

                if best_emp is None:
                    break  # не нашли подходящий слот – заказ не планируется

                end_time = best_start + datetime.timedelta(hours=op.duration_hours)
                # Бронируем ресурсы
                self.emp_busy.setdefault(best_emp.name, []).append((best_start, end_time))
                if best_mach:
                    self.machine_busy.setdefault(best_mach.name, []).append((best_start, end_time))

                self.dm.schedule.append(
                    ScheduleElement(order.order_id, op.name, best_emp.name,
                                    best_mach.name if best_mach else None,
                                    best_start, end_time)
                )
                current_time = end_time

            order.status = "Запланирован"

        self._calculate_penalties()

    def _calculate_penalties(self):
        """Штраф = 20% от стоимости изделия за каждый полный день просрочки."""
        order_end_times = {}
        for el in self.dm.schedule:
            if el.order_id not in order_end_times or el.end_time > order_end_times[el.order_id]:
                order_end_times[el.order_id] = el.end_time

        total_fine = 0.0
        for order in self.dm.orders:
            if order.status == "Запланирован" and order.order_id in order_end_times:
                actual_end = order_end_times[order.order_id]
                if actual_end > order.deadline:
                    delay = actual_end - order.deadline
                    days_late = delay.days
                    if delay.seconds > 0:
                        days_late += 1
                    pt = next((p for p in self.dm.product_types if p.type_id == order.product_type_id), None)
                    if pt:
                        fine = 0.2 * pt.cost * days_late
                        total_fine += fine
        self.dm.total_penalty = total_fine


class AppGUI(tk.Tk):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.dm = data_manager
        self.scheduler = Scheduler(self.dm)

        self.title("Система планирования производства")
        self.geometry("1000x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab_resources = ttk.Frame(self.notebook)
        self.tab_orders = ttk.Frame(self.notebook)
        self.tab_schedule = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_resources, text='Ресурсы')
        self.notebook.add(self.tab_orders, text='Заказы')
        self.notebook.add(self.tab_schedule, text='Расписание')

        self._build_resources_tab()
        self._build_orders_tab()
        self._build_schedule_tab()

        self.update_ui_lists()

    # ----- Вкладка "Ресурсы" -----
    def _build_resources_tab(self):
        frame_add = ttk.LabelFrame(self.tab_resources, text="Добавить ресурс")
        frame_add.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_add, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_res_name = ttk.Entry(frame_add, width=20)
        self.ent_res_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.cb_res_cat = ttk.Combobox(frame_add, values=["Сотрудник", "Станок"],
                                       state="readonly", width=15)
        self.cb_res_cat.current(0)
        self.cb_res_cat.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_add, text="Тип (квалификация):").grid(row=0, column=4, padx=5, pady=5)
        self.ent_res_type = ttk.Entry(frame_add, width=20)
        self.ent_res_type.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(frame_add, text="Добавить", command=self.add_resource_ui).grid(row=0, column=6, padx=10, pady=5)

        frame_list = ttk.LabelFrame(self.tab_resources, text="Список ресурсов")
        frame_list.pack(expand=True, fill='both', padx=10, pady=5)

        self.tree_resources = ttk.Treeview(frame_list, columns=("ID", "Name", "Category", "Type"),
                                           show='headings', height=15)
        self.tree_resources.heading("ID", text="ID")
        self.tree_resources.heading("Name", text="Название")
        self.tree_resources.heading("Category", text="Категория")
        self.tree_resources.heading("Type", text="Тип")
        for col, w in (("ID", 50), ("Name", 150), ("Category", 100), ("Type", 150)):
            self.tree_resources.column(col, width=w)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree_resources.yview)
        self.tree_resources.configure(yscrollcommand=scrollbar.set)
        self.tree_resources.pack(side="left", expand=True, fill='both')
        scrollbar.pack(side="right", fill='y')

    def add_resource_ui(self):
        name = self.ent_res_name.get().strip()
        cat = self.cb_res_cat.get()
        rtype = self.ent_res_type.get().strip()
        if not name or not rtype:
            messagebox.showerror("Ошибка", "Заполните все поля для ресурса!")
            return
        new_id = len(self.dm.resources) + 1
        self.dm.add_resource(Resource(new_id, name, cat, rtype))
        self.ent_res_name.delete(0, tk.END)
        self.ent_res_type.delete(0, tk.END)
        self.update_ui_lists()
        messagebox.showinfo("Успех", f"Ресурс '{name}' добавлен!")

    # ----- Вкладка "Заказы" -----
    def _build_orders_tab(self):
        frame_add = ttk.LabelFrame(self.tab_orders, text="Создать заказ")
        frame_add.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_add, text="Изделие:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_products = ttk.Combobox(frame_add, state="readonly", width=30)
        self.cb_products.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Начать не ранее (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(row=1, column=0, padx=5, pady=5)
        self.ent_start = ttk.Entry(frame_add, width=30)
        self.ent_start.insert(0, "2026-04-06 08:00")
        self.ent_start.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Дедлайн (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(row=2, column=0, padx=5, pady=5)
        self.ent_deadline = ttk.Entry(frame_add, width=30)
        self.ent_deadline.insert(0, "2026-04-07 16:00")
        self.ent_deadline.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame_add, text="Добавить заказ", command=self.add_order_ui).grid(row=3, column=0, columnspan=2, pady=10)

        frame_actions = ttk.Frame(self.tab_orders)
        frame_actions.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame_actions, text="Удалить выбранный заказ", command=self.delete_order_ui).pack(side='left', padx=5)

        frame_list = ttk.LabelFrame(self.tab_orders, text="Список заказов")
        frame_list.pack(expand=True, fill='both', padx=10, pady=5)

        self.tree_orders = ttk.Treeview(frame_list, columns=("ID", "Product", "Start", "Deadline", "Status"),
                                        show='headings', height=15)
        self.tree_orders.heading("ID", text="№ Заказа")
        self.tree_orders.heading("Product", text="ID Изделия")
        self.tree_orders.heading("Start", text="Начать с")
        self.tree_orders.heading("Deadline", text="Дедлайн")
        self.tree_orders.heading("Status", text="Статус")
        for col, w in (("ID", 80), ("Product", 80), ("Start", 150), ("Deadline", 150), ("Status", 120)):
            self.tree_orders.column(col, width=w)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree_orders.yview)
        self.tree_orders.configure(yscrollcommand=scrollbar.set)
        self.tree_orders.pack(side="left", expand=True, fill='both')
        scrollbar.pack(side="right", fill='y')

    def add_order_ui(self):
        prod_selection = self.cb_products.get()
        if not prod_selection:
            messagebox.showerror("Ошибка", "Выберите изделие!")
            return
        prod_id = int(prod_selection.split(" - ")[0])

        start_str = self.ent_start.get()
        deadline_str = self.ent_deadline.get()
        try:
            start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте: ГГГГ-ММ-ДД ЧЧ:ММ")
            return

        if start_date >= deadline:
            messagebox.showerror("Ошибка", "Дата начала должна быть раньше дедлайна!")
            return

        self.dm.add_order(prod_id, start_date, deadline)
        self.update_ui_lists()
        messagebox.showinfo("Успех", "Заказ добавлен!")

    def delete_order_ui(self):
        selected = self.tree_orders.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления!")
            return
        item = self.tree_orders.item(selected[0])
        order_id = item['values'][0]
        if messagebox.askyesno("Подтверждение", f"Удалить заказ №{order_id}?"):
            self.dm.orders = [o for o in self.dm.orders if o.order_id != order_id]
            self.update_ui_lists()
            messagebox.showinfo("Успех", "Заказ удалён!")

    # ----- Вкладка "Расписание" -----
    def _build_schedule_tab(self):
        btn_frame = ttk.Frame(self.tab_schedule)
        btn_frame.pack(fill='x', padx=10, pady=10)

        self.btn_plan = ttk.Button(btn_frame, text="Построить расписание (ASAP)", command=self.run_planning)
        self.btn_plan.pack(side='left', padx=5)

        self.lbl_penalty = ttk.Label(btn_frame, text="Суммарный штраф: 0.00 руб.",
                                     font=('Helvetica', 11, 'bold'), foreground='red')
        self.lbl_penalty.pack(side='right', padx=10)

        frame_list = ttk.LabelFrame(self.tab_schedule, text="Расписание работ")
        frame_list.pack(expand=True, fill='both', padx=10, pady=5)

        self.tree_schedule = ttk.Treeview(frame_list, columns=("Order", "Op", "Emp", "Machine", "Start", "End"),
                                          show='headings', height=20)
        self.tree_schedule.heading("Order", text="Заказ")
        self.tree_schedule.heading("Op", text="Операция")
        self.tree_schedule.heading("Emp", text="Сотрудник")
        self.tree_schedule.heading("Machine", text="Станок")
        self.tree_schedule.heading("Start", text="Начало")
        self.tree_schedule.heading("End", text="Конец")
        for col in self.tree_schedule["columns"]:
            self.tree_schedule.column(col, width=120 if col != "Op" else 150)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree_schedule.yview)
        self.tree_schedule.configure(yscrollcommand=scrollbar.set)
        self.tree_schedule.pack(side="left", expand=True, fill='both')
        scrollbar.pack(side="right", fill='y')

    def run_planning(self):
        if not self.dm.orders:
            messagebox.showwarning("Внимание", "Нет заказов для планирования!")
            return
        if not self.dm.resources:
            messagebox.showwarning("Внимание", "Нет ресурсов для планирования!")
            return
        try:
            self.scheduler.schedule_orders()
            self.update_ui_lists()
            self.lbl_penalty.config(text=f"Суммарный штраф: {self.dm.total_penalty:.2f} руб.")
            self.notebook.select(self.tab_schedule)
            messagebox.showinfo("Готово", "Расписание успешно построено!")
        except Exception as e:
            messagebox.showerror("Ошибка алгоритма", str(e))

    def update_ui_lists(self):
        # Обновление списка ресурсов
        for row in self.tree_resources.get_children():
            self.tree_resources.delete(row)
        for r in self.dm.resources:
            self.tree_resources.insert('', 'end', values=(r.res_id, r.name, r.res_category, r.res_type))

        # Обновление выпадающего списка продуктов
        self.cb_products['values'] = [f"{p.type_id} - {p.name}" for p in self.dm.product_types]
        if self.dm.product_types and not self.cb_products.get():
            self.cb_products.current(0)

        # Обновление списка заказов
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)
        for o in self.dm.orders:
            self.tree_orders.insert('', 'end', values=(
                o.order_id, o.product_type_id,
                o.start_date.strftime("%Y-%m-%d %H:%M"),
                o.deadline.strftime("%Y-%m-%d %H:%M"),
                o.status
            ))

        # Обновление расписания
        for row in self.tree_schedule.get_children():
            self.tree_schedule.delete(row)
        for el in self.dm.schedule:
            self.tree_schedule.insert('', 'end', values=(
                f"#{el.order_id}", el.op_name, el.emp_name, el.machine_name,
                el.start_time.strftime("%Y-%m-%d %H:%M"),
                el.end_time.strftime("%Y-%m-%d %H:%M")
            ))


if __name__ == "__main__":
    dm = DataManager()
    dm.load_all_from_csv()      # данные из CSV или автосоздание
    app = AppGUI(dm)
    app.mainloop()
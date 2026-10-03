import sys
import subprocess
import importlib.util
import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QComboBox,
    QTextEdit,
    QMessageBox,
    QToolBar,
)


# ============================================================
# PROJECT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SOLVER_FILE = BASE_DIR / "cube_solver_rev3_samson.py"
TEST_FILE = BASE_DIR / "test_cube_solver_rev3_samson.py"

# GUI-only display conversion factors. The structural solver/database
# remains in its native Metric units (m, kN, MPa).
M_TO_FT = 3.280839895013123
KN_TO_KIP = 0.22480894387096
MPA_TO_KSI = 0.14503773773020923



# ============================================================
# VISUALIZATION FILES
# ============================================================

VISUALIZATIONS = {
    "Load Case 1 — Dead Load":
        "rev3_load_case_1_samson.png",

    "Load Case 2":
        "rev3_load_case_2_samson.png",

    "Load Case 3":
        "rev3_load_case_3_samson.png",

    "Load Case 4":
        "rev3_load_case_4_samson.png",

    "Load Case 5":
        "rev3_load_case_5_samson.png",

    "Load Case 6":
        "rev3_load_case_6_samson.png",

    "Load Case 7":
        "rev3_load_case_7_samson.png",

    "Load Case 8":
        "rev3_load_case_8_samson.png",

    "Load Case 9 — Temperature":
        "rev3_load_case_9_samson.png",

    "COMB1 — LRFD":
        "rev3_combination_1_samson.png",

    "COMB13 — ASD":
        "rev3_combination_13_samson.png",
}


# ============================================================
# MAIN WINDOW
# ============================================================

class Rev3Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CUBE STRUCTURAL SOLVER — REV3"
        )

        self.setMinimumSize(1280, 760)
        self.resize(1600, 920)

        self.build_menu()
        self.build_toolbar()
        self.build_ui()
        self.apply_style()

        # GUI display state. The solver/database remains Metric.
        self.display_units = "Metric"

        # Keep the selector and internal GUI state synchronized.
        if hasattr(self, "unit_combo"):
            self.unit_combo.blockSignals(True)
            self.unit_combo.setCurrentIndex(0)
            self.unit_combo.blockSignals(False)

        # Read-only model metadata from the actual REV3 source.
        self.refresh_model_information()
        self.populate_model_tree()
        self.refresh_selection_properties()

        self.statusBar().showMessage(
            "REV3 Structural Command Center — Ready | GUI display layer"
        )

        # Show first available visualization
        self.load_visualization(
            "COMB13 — ASD"
        )

    # ========================================================
    # MENU
    # ========================================================

    def build_menu(self):

        menu_bar = self.menuBar()

        # FILE
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Show the active REV3 project folder")
        open_action.triggered.connect(self.open_project)

        reload_file_action = QAction("Reload Model", self)
        reload_file_action.setShortcut("Ctrl+R")
        reload_file_action.setStatusTip("Refresh model metadata from the REV3 solver")
        reload_file_action.triggered.connect(self.reload_solver)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close the REV3 dashboard")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(reload_file_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # MODEL
        model_menu = menu_bar.addMenu("Model")

        refresh_model_action = QAction("Refresh Model", self)
        refresh_model_action.setStatusTip("Refresh model metadata and the Model Explorer")
        refresh_model_action.triggered.connect(self.reload_solver)

        model_info_action = QAction("Model Information", self)
        model_info_action.setStatusTip("Show actual REV3 model metadata")
        model_info_action.triggered.connect(self.show_model_information)

        model_menu.addAction(refresh_model_action)
        model_menu.addAction(model_info_action)

        # VIEW
        view_menu = menu_bar.addMenu("View")

        model_action = QAction("3D Model", self)
        model_action.setShortcut("F3")
        model_action.setStatusTip("Refresh the active structural visualization")
        model_action.triggered.connect(self.show_model)

        refresh_view_action = QAction("Refresh Visualization", self)
        refresh_view_action.setShortcut("F5")
        refresh_view_action.setStatusTip("Redraw the active visualization")
        refresh_view_action.triggered.connect(self.show_model)

        view_menu.addAction(model_action)
        view_menu.addAction(refresh_view_action)

        # ANALYSIS
        analysis_menu = menu_bar.addMenu("Analysis")

        solve_action = QAction("Solve Model", self)
        solve_action.setShortcut("F6")
        solve_action.setStatusTip("Run the REV3 solver")
        solve_action.triggered.connect(self.solve_model)

        validate_action = QAction("Validate Model", self)
        validate_action.setShortcut("F7")
        validate_action.setStatusTip("Run the REV3 validation suite")
        validate_action.triggered.connect(self.validate_model)

        analysis_menu.addAction(solve_action)
        analysis_menu.addAction(validate_action)

        # RESULTS
        results_menu = menu_bar.addMenu("Results")

        results_action = QAction("View Visualization", self)
        results_action.setStatusTip("Show the active load-case or combination visualization")
        results_action.triggered.connect(self.show_model)

        results_panel_action = QAction("Analysis Results", self)
        results_panel_action.setShortcut("F8")
        results_panel_action.setStatusTip("Open the REV3 analysis-scope summary")
        results_panel_action.triggered.connect(self.show_analysis_results)

        results_menu.addAction(results_action)
        results_menu.addAction(results_panel_action)

        # TOOLS
        tools_menu = menu_bar.addMenu("Tools")

        units_action = QAction("Display Units", self)
        units_action.setStatusTip("Set the dashboard display to Metric or Imperial")
        units_action.triggered.connect(self.focus_unit_selector)

        console_action = QAction("Show Console", self)
        console_action.setStatusTip("Show the REV3 dashboard console")
        console_action.triggered.connect(self.show_console)

        tools_menu.addAction(units_action)
        tools_menu.addAction(console_action)

        # HELP
        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About REV3", self)
        about_action.setStatusTip("About the REV3 dashboard")
        about_action.triggered.connect(self.show_about)

        scope_action = QAction("Solver Scope", self)
        scope_action.setStatusTip("Show what the current REV3 solver does and does not calculate")
        scope_action.triggered.connect(self.show_solver_scope)

        help_menu.addAction(about_action)
        help_menu.addAction(scope_action)

    # ========================================================
    # TOOLBAR
    # ========================================================

    def build_toolbar(self):

        toolbar = QToolBar(
            "REV3 Toolbar"
        )

        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        self.addToolBar(toolbar)

        solve = QAction(
            "▶  Solve",
            self
        )
        solve.triggered.connect(
            self.solve_model
        )

        validate = QAction(
            "✓  Validate",
            self
        )
        validate.triggered.connect(
            self.validate_model
        )

        reload_action = QAction(
            "↻  Reload",
            self
        )
        reload_action.triggered.connect(
            self.reload_solver
        )

        model = QAction(
            "◇  3D Model",
            self
        )
        model.triggered.connect(
            self.show_model
        )

        toolbar.addAction(solve)
        toolbar.addAction(validate)
        toolbar.addAction(reload_action)
        toolbar.addSeparator()
        toolbar.addAction(model)

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            10, 10, 10, 10
        )

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        # ====================================================
        # LEFT — MODEL EXPLORER
        # ====================================================

        left_panel = QFrame()

        left_layout = QVBoxLayout(
            left_panel
        )

        title = QLabel(
            "MODEL EXPLORER"
        )

        title.setObjectName(
            "panelTitle"
        )

        left_layout.addWidget(
            title
        )

        self.model_tree = QTreeWidget()

        self.model_tree.setHeaderHidden(
            True
        )

        # Interactive explorer: selecting a node/member/support updates the
        # property panel directly from the read-only model metadata.
        self.model_tree.itemClicked.connect(
            self.on_model_tree_item_clicked
        )

        self.populate_model_tree()

        left_layout.addWidget(
            self.model_tree,
            1
        )

        selection_frame = QFrame()
        selection_frame.setObjectName(
            "infoCard"
        )
        selection_layout = QVBoxLayout(selection_frame)
        selection_title = QLabel(
            "SELECTION PROPERTIES"
        )
        selection_title.setObjectName(
            "cardTitle"
        )
        selection_layout.addWidget(selection_title)

        self.selection_value = QLabel(
            "Select a node, member, or support"
        )
        self.selection_value.setObjectName(
            "cardValue"
        )
        self.selection_value.setWordWrap(True)
        selection_layout.addWidget(self.selection_value)

        left_layout.addWidget(selection_frame)

        # ====================================================
        # CENTER — MODEL VIEW
        # ====================================================

        center_panel = QFrame()

        center_layout = QVBoxLayout(
            center_panel
        )

        center_title = QLabel(
            "CUBE STRUCTURAL MODEL"
        )

        center_title.setObjectName(
            "panelTitle"
        )

        center_layout.addWidget(
            center_title
        )

        # Visualization selector

        selector_layout = QHBoxLayout()

        selector_label = QLabel(
            "Visualization:"
        )

        selector_label.setObjectName(
            "selectorLabel"
        )

        self.visualization_combo = QComboBox()

        self.visualization_combo.addItems(
            list(VISUALIZATIONS.keys())
        )

        self.visualization_combo.setCurrentText(
            "COMB13 — ASD"
        )

        self.visualization_combo.currentTextChanged.connect(
            self.load_visualization
        )

        selector_layout.addWidget(
            selector_label
        )

        selector_layout.addWidget(
            self.visualization_combo,
            1
        )

        center_layout.addLayout(
            selector_layout
        )

        # Image area

        self.model_display = QLabel()

        self.model_display.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.model_display.setMinimumSize(
            500,
            500
        )

        self.model_display.setObjectName(
            "modelDisplay"
        )

        center_layout.addWidget(
            self.model_display,
            1
        )

        # ====================================================
        # RIGHT — ANALYSIS DASHBOARD
        # ====================================================

        right_panel = QFrame()

        right_layout = QVBoxLayout(
            right_panel
        )

        dashboard_title = QLabel(
            "ANALYSIS DASHBOARD"
        )

        dashboard_title.setObjectName(
            "panelTitle"
        )

        right_layout.addWidget(
            dashboard_title
        )

        # Dynamic model information

        unit_card = self.create_card(
            "UNIT SYSTEM",
            "Reading model..."
        )
        self.unit_card_value = unit_card.findChild(QLabel, "cardValue")
        right_layout.addWidget(unit_card)

        model_card = self.create_card(
            "MODEL",
            "Reading model..."
        )
        self.model_card_value = model_card.findChild(QLabel, "cardValue")
        right_layout.addWidget(model_card)

        material_card = self.create_card(
            "MATERIAL / SECTION",
            "Reading model..."
        )
        self.material_card_value = material_card.findChild(QLabel, "cardValue")
        right_layout.addWidget(material_card)

        load_count_card = self.create_card(
            "LOAD FRAMEWORK",
            "Reading REV3..."
        )
        self.load_count_card_value = load_count_card.findChild(QLabel, "cardValue")
        right_layout.addWidget(load_count_card)

        scope_card = self.create_card(
            "ANALYSIS SCOPE",
            "Reading REV3..."
        )
        self.scope_card_value = scope_card.findChild(QLabel, "cardValue")
        right_layout.addWidget(scope_card)

        support_card = self.create_card(
            "SUPPORT CONDITIONS",
            "Pinned Supports\nNodes 1–4"
        )
        right_layout.addWidget(support_card)

        # Validation card

        self.validation_value = QLabel(
            "NOT RUN"
        )

        self.validation_value.setObjectName(
            "cardValue"
        )

        validation_frame = QFrame()

        validation_frame.setObjectName(
            "infoCard"
        )

        validation_layout = QVBoxLayout(
            validation_frame
        )

        validation_title = QLabel(
            "VALIDATION"
        )

        validation_title.setObjectName(
            "cardTitle"
        )

        validation_layout.addWidget(
            validation_title
        )

        validation_layout.addWidget(
            self.validation_value
        )

        right_layout.addWidget(
            validation_frame
        )

        # Solver status

        self.solver_status = QLabel(
            "READY"
        )

        self.solver_status.setObjectName(
            "cardValue"
        )

        status_frame = QFrame()

        status_frame.setObjectName(
            "infoCard"
        )

        status_layout = QVBoxLayout(
            status_frame
        )

        status_title = QLabel(
            "SOLVER STATUS"
        )

        status_title.setObjectName(
            "cardTitle"
        )

        status_layout.addWidget(
            status_title
        )

        status_layout.addWidget(
            self.solver_status
        )

        right_layout.addWidget(
            status_frame
        )

        # Current visualization

        self.current_case_value = QLabel(
            "COMB13 — ASD"
        )

        self.current_case_value.setObjectName(
            "cardValue"
        )

        current_frame = QFrame()

        current_frame.setObjectName(
            "infoCard"
        )

        current_layout = QVBoxLayout(
            current_frame
        )

        current_title = QLabel(
            "ACTIVE VIEW"
        )

        current_title.setObjectName(
            "cardTitle"
        )

        current_layout.addWidget(
            current_title
        )

        current_layout.addWidget(
            self.current_case_value
        )

        right_layout.addWidget(
            current_frame
        )

        # Units

        units_label = QLabel(
            "Display Units"
        )

        right_layout.addWidget(
            units_label
        )

        self.unit_combo = QComboBox()

        self.unit_combo.addItems(
            [
                "Metric (m, kN)",
                "Imperial (ft, kip)"
            ]
        )

        # Use the index signal so the display state is updated reliably
        # regardless of the visible text/formatting of the combo box.
        self.unit_combo.currentIndexChanged.connect(
            self.change_units
        )

        right_layout.addWidget(
            self.unit_combo
        )

        # Buttons

        solve_button = QPushButton(
            "▶  SOLVE MODEL"
        )

        solve_button.clicked.connect(
            self.solve_model
        )

        right_layout.addWidget(
            solve_button
        )

        validate_button = QPushButton(
            "✓  VALIDATE MODEL"
        )

        validate_button.clicked.connect(
            self.validate_model
        )

        right_layout.addWidget(
            validate_button
        )

        results_button = QPushButton(
            "▣  VIEW RESULTS"
        )

        results_button.clicked.connect(
            self.show_analysis_results
        )

        right_layout.addWidget(
            results_button
        )

        right_layout.addStretch()

        # ====================================================
        # SPLITTER
        # ====================================================

        splitter.addWidget(
            left_panel
        )

        splitter.addWidget(
            center_panel
        )

        splitter.addWidget(
            right_panel
        )

        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        left_panel.setMinimumWidth(250)
        center_panel.setMinimumWidth(560)
        right_panel.setMinimumWidth(330)

        splitter.setSizes(
            [
                285,
                900,
                365
            ]
        )

        main_layout.addWidget(
            splitter
        )

    # ========================================================
    # REV3 MODEL DATA
    # ========================================================

    def load_rev3_model_data(self):
        """Read model metadata from the actual REV3/Rev.2 model source.

        This is a read-only GUI bridge. It does not modify the solver,
        load definitions, or validation logic.
        """
        data = {
            "nodes": None,
            "members": None,
            "dof": None,
            "dimensions": None,
            "material": None,
            "section": None,
            "units": "Metric",
            "load_cases": None,
            "combinations": None,
            "diaphragm": None,
            "scope": None,
            "node_records": {},
            "member_records": {},
        }

        try:
            if not SOLVER_FILE.exists():
                return data

            spec = importlib.util.spec_from_file_location(
                "rev3_dashboard_solver",
                SOLVER_FILE
            )
            if spec is None or spec.loader is None:
                return data

            module = importlib.util.module_from_spec(spec)
            # Register the module before execution. This is required by
            # dataclasses/type resolution inside cube_solver_rev3_samson.py.
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # The REV3 module intentionally reuses the Rev.2 database model.
            model = module.get_rev2_model()

            nodes = getattr(model, "nodes", None)
            members = getattr(model, "members", None)

            if nodes is not None:
                data["nodes"] = len(nodes)
                data["dof"] = len(nodes) * len(getattr(module, "DOF_NAMES", ()))

                # Geometry extents from actual node coordinates.
                try:
                    coords = model.node_coordinates
                    xyz = [
                        [float(c[0]), float(c[1]), float(c[2])]
                        for c in coords.values()
                    ]
                except Exception:
                    xyz = [
                        [
                            float(row["X (m)"]),
                            float(row["Y (m)"]),
                            float(row["Z (m)"]),
                        ]
                        for _, row in nodes.iterrows()
                    ]

                if xyz:
                    spans = [
                        max(c[i] for c in xyz) - min(c[i] for c in xyz)
                        for i in range(3)
                    ]
                    data["dimensions"] = spans

                # Preserve actual node coordinates for the interactive
                # explorer. Values remain in the solver's native Metric units.
                data["node_records"] = self._extract_node_records(
                    nodes, model
                )

            if members is not None:
                data["members"] = len(members)
                data["member_records"] = self._extract_member_records(
                    members, model
                )

            data["material"] = getattr(
                model, "MATERIAL_LABEL", None
            ) or getattr(
                model, "MATERIAL_NAME", None
            )

            data["section"] = getattr(
                model, "SECTION_LABEL", None
            )

            # Use the REV3 unit declarations when available.
            length_unit = getattr(module, "UNIT_LENGTH", "m")
            force_unit = getattr(module, "UNIT_FORCE", "kN")
            data["units"] = f"Metric ({length_unit}, {force_unit})"

            load_cases = getattr(module, "LOAD_CASES_REV3", None)
            if load_cases is not None:
                data["load_cases"] = len(load_cases) + 1  # LC9 is separate.

            combinations = getattr(module, "LOAD_COMBINATIONS_REV3", None)
            if combinations is not None:
                data["combinations"] = len(combinations)

            diaphragm = getattr(module, "ROOF_DIAPHRAGM_REV3", None)
            if diaphragm is not None:
                master = getattr(diaphragm, "master_node", None)
                slaves = getattr(diaphragm, "slave_nodes", None)
                if master is not None and slaves is not None:
                    data["diaphragm"] = (
                        f"Master N{master}; "
                        f"Slaves N{', N'.join(str(x) for x in slaves)}"
                    )

            data["scope"] = (
                "Load definition, validation, combinations and visualization"
            )

        except Exception as exc:
            self.console_message(
                f"Model metadata: using unavailable fields ({exc})"
            )

        return data

    def refresh_model_information(self):
        """Refresh GUI metadata and render it in the selected display units.

        The REV3 solver/database remains Metric. This method only converts
        values shown by the dashboard; it never changes solver inputs.
        """
        self.model_data = self.load_rev3_model_data()
        self.update_unit_display()

    def update_unit_display(self):
        """Update all dashboard unit-dependent text from stored Metric data."""
        d = self.model_data

        node_count = d["nodes"] if d["nodes"] is not None else "—"
        member_count = d["members"] if d["members"] is not None else "—"
        dof_count = d["dof"] if d["dof"] is not None else "—"

        dimensions = d.get("dimensions")
        if dimensions:
            if self.display_units == "Imperial":
                converted = [v * M_TO_FT for v in dimensions]
                dim_text = " × ".join(f"{v:.3f}" for v in converted) + " ft"
            else:
                dim_text = " × ".join(f"{v:g}" for v in dimensions) + " m"
        else:
            dim_text = "Unavailable"

        self.model_card_value.setText(
            f"{node_count} Nodes  •  {member_count} Members\n"
            f"{dof_count} DOF  •  {dim_text}"
        )

        if self.display_units == "Imperial":
            self.unit_card_value.setText("Imperial (ft, kip)")
        else:
            self.unit_card_value.setText("Metric (m, kN)")

        material = d["material"] or "Unavailable"
        section = d["section"] or "Unavailable"
        self.material_card_value.setText(
            f"{material}\nSection: {section}"
        )

        if d["diaphragm"]:
            self.scope_card_value.setText(
                f"{d['scope']}\n{d['diaphragm']}"
            )
        else:
            self.scope_card_value.setText(
                d["scope"] or "Unavailable"
            )

        self.load_count_card_value.setText(
            f"{d['load_cases'] if d['load_cases'] is not None else '—'} "
            f"Load Cases  •  "
            f"{d['combinations'] if d['combinations'] is not None else '—'} "
            f"Combinations"
        )

    # ========================================================
    # MODEL TREE
    # ========================================================

    def populate_model_tree(self):

        self.model_tree.clear()

        data = getattr(self, "model_data", {})
        node_count = data.get("nodes") or 8
        member_count = data.get("members") or 12
        load_count = data.get("load_cases") or 9
        comb_count = data.get("combinations") or 30

        nodes = QTreeWidgetItem(
            [f"Nodes ({node_count})"]
        )
        for i in range(1, int(node_count) + 1):
            child = QTreeWidgetItem(nodes, [f"Node {i}"])
            child.setData(0, Qt.ItemDataRole.UserRole, f"node:{i}")

        members = QTreeWidgetItem(
            [f"Members ({member_count})"]
        )
        for i in range(1, int(member_count) + 1):
            child = QTreeWidgetItem(members, [f"Member {i}"])
            child.setData(0, Qt.ItemDataRole.UserRole, f"member:{i}")

        supports = QTreeWidgetItem(
            ["Supports"]
        )
        for i in range(1, 5):
            child = QTreeWidgetItem(
                supports,
                [f"Pinned — Node {i}"]
            )
            child.setData(0, Qt.ItemDataRole.UserRole, f"support:{i}")

        loads = QTreeWidgetItem(
            [f"Load Cases ({load_count})"]
        )
        for i in range(1, int(load_count) + 1):
            label = f"Load Case {i}"
            if i == 9:
                label = "Load Case 9 — Temperature"
            QTreeWidgetItem(loads, [label])

        combinations = QTreeWidgetItem(
            [f"Combinations ({comb_count})"]
        )
        for i in range(1, int(comb_count) + 1):
            label = f"COMB{i}"
            if i == 1:
                label += " — LRFD"
            elif i == 13:
                label += " — ASD"
            QTreeWidgetItem(combinations, [label])

        materials = QTreeWidgetItem(
            ["Materials"]
        )
        material = data.get("material") or "Material database"
        section = data.get("section") or "Section database"
        QTreeWidgetItem(materials, [str(material)])
        QTreeWidgetItem(materials, [str(section)])

        for item in (
            nodes,
            members,
            supports,
            loads,
            combinations,
            materials,
        ):
            self.model_tree.addTopLevelItem(item)

        self.model_tree.expandAll()

    # ========================================================
    # INTERACTIVE MODEL PROPERTIES
    # ========================================================

    @staticmethod
    def _normalize_key(value):
        return re.sub(r"[^a-z0-9]", "", str(value).lower())

    @staticmethod
    def _record_value(row, candidates):
        """Return the first non-empty value matching candidate field names."""
        if row is None:
            return None
        try:
            keys = list(row.index)
        except Exception:
            keys = []
        normalized = {
            Rev3Dashboard._normalize_key(k): k for k in keys
        }
        for candidate in candidates:
            key = normalized.get(
                Rev3Dashboard._normalize_key(candidate)
            )
            if key is not None:
                try:
                    value = row[key]
                    if value is not None and str(value).strip() not in ("", "nan", "None"):
                        return value
                except Exception:
                    pass
        return None

    @staticmethod
    def _clean_id(value, fallback):
        if value is None:
            return fallback
        try:
            if float(value).is_integer():
                return int(float(value))
        except Exception:
            pass
        match = re.search(r"(\d+)", str(value))
        return int(match.group(1)) if match else fallback

    def _extract_node_records(self, nodes, model):
        records = {}
        # Preferred source: the model's explicit node_coordinates mapping.
        try:
            coords = getattr(model, "node_coordinates", None)
            if coords is not None:
                for key, value in coords.items():
                    node_id = self._clean_id(key, len(records) + 1)
                    records[node_id] = {
                        "x": float(value[0]),
                        "y": float(value[1]),
                        "z": float(value[2]),
                    }
                if records:
                    return records
        except Exception:
            pass

        # Fallback for the tabular Rev.2 node database.
        try:
            for index, row in nodes.iterrows():
                node_id = self._clean_id(
                    self._record_value(row, ["Node", "Node ID", "Node_ID", "ID"]),
                    self._clean_id(index, len(records) + 1),
                )
                x = self._record_value(row, ["X (m)", "X", "X Coordinate"])
                y = self._record_value(row, ["Y (m)", "Y", "Y Coordinate"])
                z = self._record_value(row, ["Z (m)", "Z", "Z Coordinate"])
                if x is not None and y is not None and z is not None:
                    records[node_id] = {
                        "x": float(x),
                        "y": float(y),
                        "z": float(z),
                    }
        except Exception:
            pass
        return records

    def _extract_member_records(self, members, model):
        records = {}
        # The Rev.2 database is normally tabular; keep this intentionally
        # flexible so GUI changes do not depend on one column spelling.
        try:
            iterator = members.iterrows()
        except Exception:
            iterator = []

        try:
            for index, row in iterator:
                member_id = self._clean_id(
                    self._record_value(row, [
                        "Member", "Member ID", "Member_ID", "ID"
                    ]),
                    self._clean_id(index, len(records) + 1),
                )
                start = self._record_value(row, [
                    "Start Node", "Start_Node", "Node I", "Node_i",
                    "I Node", "I", "Start"
                ])
                end = self._record_value(row, [
                    "End Node", "End_Node", "Node J", "Node_j",
                    "J Node", "J", "End"
                ])
                beta = self._record_value(row, [
                    "Beta (deg)", "Beta", "β (deg)", "Beta Angle",
                    "Beta Angle (deg)"
                ])

                release_values = []
                try:
                    for key in row.index:
                        normalized = self._normalize_key(key)
                        if "release" in normalized:
                            value = row[key]
                            if str(value).strip() not in ("", "nan", "None"):
                                release_values.append(f"{key}: {value}")
                except Exception:
                    pass

                records[member_id] = {
                    "start": self._clean_id(start, None),
                    "end": self._clean_id(end, None),
                    "beta": beta,
                    "releases": release_values,
                }
        except Exception:
            pass
        return records

    def on_model_tree_item_clicked(self, item, column=0):
        """Render actual model properties for the selected explorer item."""
        token = item.data(0, Qt.ItemDataRole.UserRole)
        if not token or not hasattr(self, "selection_value"):
            return

        kind, _, raw_id = str(token).partition(":")
        try:
            item_id = int(raw_id)
        except ValueError:
            return

        d = self.model_data

        if kind == "node":
            record = d.get("node_records", {}).get(item_id)
            if not record:
                text = f"NODE {item_id}\n\nCoordinates unavailable in model metadata."
            else:
                if self.display_units == "Imperial":
                    x = record["x"] * M_TO_FT
                    y = record["y"] * M_TO_FT
                    z = record["z"] * M_TO_FT
                    unit = "ft"
                else:
                    x, y, z = record["x"], record["y"], record["z"]
                    unit = "m"
                text = (
                    f"NODE {item_id}\n"
                    f"Coordinates\n"
                    f"X = {x:.3f} {unit}\n"
                    f"Y = {y:.3f} {unit}\n"
                    f"Z = {z:.3f} {unit}\n\n"
                    f"DOF\n"
                    f"UX • UY • UZ\n"
                    f"RX • RY • RZ"
                )

        elif kind == "member":
            record = d.get("member_records", {}).get(item_id, {})
            start = record.get("start")
            end = record.get("end")
            beta = record.get("beta")
            beta_text = "Unavailable" if beta is None else str(beta)
            if start is None:
                start = "Unavailable"
            if end is None:
                end = "Unavailable"
            releases = record.get("releases") or []
            release_text = "\n".join(releases) if releases else "As defined in model"
            text = (
                f"MEMBER {item_id}\n"
                f"Start Node: {start}\n"
                f"End Node: {end}\n\n"
                f"Material\n{d.get('material') or 'Unavailable'}\n\n"
                f"Section\n{d.get('section') or 'Unavailable'}\n\n"
                f"Beta Angle\n{beta_text}°\n\n"
                f"End Releases\n{release_text}"
            )

        elif kind == "support":
            text = (
                f"SUPPORT — NODE {item_id}\n"
                f"Type\nPinned\n\n"
                f"Translational DOF\n"
                f"UX • UY • UZ\n\n"
                f"Rotational DOF\n"
                f"RX • RY • RZ"
            )
        else:
            return

        self.selection_value.setText(text)

    def refresh_selection_properties(self):
        """Re-render the current selection after unit/model refreshes."""
        item = self.model_tree.currentItem() if hasattr(self, "model_tree") else None
        if item is not None:
            self.on_model_tree_item_clicked(item, 0)

    # ========================================================
    # CARD
    # ========================================================

    def create_card(
        self,
        title,
        value
    ):

        frame = QFrame()

        frame.setObjectName(
            "infoCard"
        )

        layout = QVBoxLayout(
            frame
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "cardTitle"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            "cardValue"
        )

        value_label.setWordWrap(
            True
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        return frame

    # ========================================================
    # LOAD VISUALIZATION
    # ========================================================

    def load_visualization(
        self,
        case_name
    ):

        filename = VISUALIZATIONS.get(
            case_name
        )

        if not filename:
            return

        image_path = BASE_DIR / filename

        if not image_path.exists():

            self.model_display.setText(
                "Visualization not found:\n\n"
                + filename
            )

            return

        pixmap = QPixmap(
            str(image_path)
        )

        if pixmap.isNull():

            self.model_display.setText(
                "Unable to load visualization."
            )

            return

        self.current_case_value.setText(
            case_name
        )

        self.update_model_image(
            pixmap
        )

        self.statusBar().showMessage(
            f"Displaying {case_name}"
        )

    # ========================================================
    # RESIZE IMAGE
    # ========================================================

    def update_model_image(
        self,
        pixmap
    ):

        if pixmap.isNull():
            return

        scaled = pixmap.scaled(
            self.model_display.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.model_display.setPixmap(
            scaled
        )

        self.current_pixmap = pixmap

    # ========================================================
    # RESIZE EVENT
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "current_pixmap"
        ):

            self.update_model_image(
                self.current_pixmap
            )

    # ========================================================
    # SOLVER
    # ========================================================

    def solve_model(self):

        self.solver_status.setText(
            "RUNNING..."
        )

        self.statusBar().showMessage(
            "Running REV3 solver..."
        )

        self.console_message(
            "=== REV3 SOLVER ==="
        )

        if not SOLVER_FILE.exists():

            self.console_message(
                "ERROR: Solver file not found."
            )

            self.solver_status.setText(
                "ERROR"
            )

            return

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    str(SOLVER_FILE)
                ],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )

            if result.stdout:

                self.console_message(
                    result.stdout
                )

            if result.stderr:

                self.console_message(
                    "\n--- STDERR ---\n"
                    + result.stderr
                )

            if result.returncode == 0:

                self.solver_status.setText(
                    "COMPLETED"
                )

                self.statusBar().showMessage(
                    "REV3 solver completed."
                )

                # Refresh visualization
                self.load_visualization(
                    self.visualization_combo.currentText()
                )

            else:

                self.solver_status.setText(
                    "ERROR"
                )

                self.statusBar().showMessage(
                    "REV3 solver returned an error."
                )

        except Exception as exc:

            self.solver_status.setText(
                "ERROR"
            )

            self.console_message(
                f"ERROR: {exc}"
            )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_model(self):

        self.validation_value.setText(
            "RUNNING..."
        )

        self.solver_status.setText(
            "VALIDATING..."
        )

        self.statusBar().showMessage(
            "Running 95-test REV3 validation..."
        )

        self.console_message(
            "=== REV3 VALIDATION ==="
        )

        if not TEST_FILE.exists():

            self.validation_value.setText(
                "TEST FILE NOT FOUND"
            )

            return

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    str(TEST_FILE)
                ],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            self.console_message(
                output
            )

            if result.returncode == 0:

                self.validation_value.setText(
                    "✓ 95 / 95 PASSED"
                )

                self.solver_status.setText(
                    "VALIDATED"
                )

                self.statusBar().showMessage(
                    "REV3 validation complete — 95 / 95 tests passed."
                )

            else:

                self.validation_value.setText(
                    "✗ VALIDATION FAILED"
                )

                self.solver_status.setText(
                    "CHECK ERRORS"
                )

                self.statusBar().showMessage(
                    "REV3 validation reported errors."
                )

        except Exception as exc:

            self.validation_value.setText(
                "ERROR"
            )

            self.solver_status.setText(
                "ERROR"
            )

            self.console_message(
                f"ERROR: {exc}"
            )

    # ========================================================
    # ANALYSIS RESULTS
    # ========================================================

    def show_analysis_results(self):
        """Open a read-only summary of the REV3 analysis framework.

        This panel reports only information supported by the current REV3
        model and validation workflow. It does not invent structural
        response quantities that are outside the solver's implemented scope.
        """
        d = getattr(self, "model_data", {})
        unit = "Imperial (ft, kip)" if self.display_units == "Imperial" else "Metric (m, kN)"
        dimensions = d.get("dimensions")
        if dimensions:
            if self.display_units == "Imperial":
                dim_values = [v * M_TO_FT for v in dimensions]
                dim_text = " × ".join(f"{v:.3f}" for v in dim_values) + " ft"
            else:
                dim_text = " × ".join(f"{v:g}" for v in dimensions) + " m"
        else:
            dim_text = "Unavailable"

        active_view = self.visualization_combo.currentText()
        validation = self.validation_value.text()
        validation_state = "NOT RUN" if validation == "NOT RUN" else validation
        diaphragm = d.get("diaphragm") or "Not reported"

        dialog = QDialog(self)
        dialog.setWindowTitle("REV3 — Analysis Results")
        dialog.resize(620, 610)

        layout = QVBoxLayout(dialog)

        title = QLabel("REV3 ANALYSIS RESULTS")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        summary = QTextEdit()
        summary.setReadOnly(True)
        summary.setObjectName("resultsText")
        summary.setPlainText(
            f"ACTIVE VIEW\n{active_view}\n\n"
            f"DISPLAY UNITS\n{unit}\n\n"
            f"MODEL\n"
            f"{d.get('nodes', '—')} Nodes  •  {d.get('members', '—')} Members\n"
            f"{d.get('dof', '—')} DOF  •  {dim_text}\n\n"
            f"MATERIAL / SECTION\n"
            f"{d.get('material') or 'Unavailable'}\n"
            f"Section: {d.get('section') or 'Unavailable'}\n\n"
            f"LOAD FRAMEWORK\n"
            f"{d.get('load_cases', '—')} Load Cases  •  {d.get('combinations', '—')} Combinations\n\n"
            f"TEMPERATURE\n"
            f"Load Case 9 — Temperature\n"
            f"Thermal loading is included in the REV3 framework.\n\n"
            f"DIAPHRAGM\n"
            f"{diaphragm}\n\n"
            f"VALIDATION\n"
            f"{validation_state}\n\n"
            f"IMPLEMENTED SCOPE\n"
            f"✓ Load definition\n"
            f"✓ Load-case validation\n"
            f"✓ Load combinations\n"
            f"✓ Temperature-load framework\n"
            f"✓ Visualization\n\n"
            f"OUT OF SCOPE\n"
            f"• Stiffness solution / displacement response\n"
            f"• Support reactions\n"
            f"• Member-force response\n"
            f"• Drift results\n\n"
            f"Note: This dashboard reports the implemented REV3 scope; it does not fabricate structural response results."
        )
        layout.addWidget(summary)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    # ========================================================
    # 3D MODEL
    # ========================================================

    def show_model(self):

        self.load_visualization(
            self.visualization_combo.currentText()
        )

    # ========================================================
    # UNITS
    # ========================================================

    def change_units(
        self,
        value
    ):
        """Switch dashboard display units without modifying the solver model.

        This slot accepts the combo-box index.  Keeping the GUI unit state
        independent from the solver's Metric database prevents a refresh or
        visualization change from accidentally reverting the dashboard label.
        """
        if isinstance(value, int):
            self.display_units = "Imperial" if value == 1 else "Metric"
        else:
            self.display_units = (
                "Imperial" if str(value).startswith("Imperial") else "Metric"
            )

        self.update_unit_display()
        self.refresh_selection_properties()

        if self.display_units == "Imperial":
            self.statusBar().showMessage(
                "Display units: Imperial (ft, kip) — dashboard values converted from Metric"
            )
        else:
            self.statusBar().showMessage(
                "Display units: Metric (m, kN)"
            )

    # ========================================================
    # RELOAD
    # ========================================================

    def reload_solver(self):

        self.solver_status.setText(
            "READY"
        )

        self.refresh_model_information()
        self.populate_model_tree()
        self.refresh_selection_properties()

        self.statusBar().showMessage(
            "REV3 model metadata refreshed."
        )

    # ========================================================
    # CONSOLE
    # ========================================================

    def console_message(
        self,
        message
    ):

        if not hasattr(
            self,
            "console"
        ):

            self.console = QTextEdit()

            self.console.setReadOnly(
                True
            )

            self.console.setWindowTitle(
                "REV3 Console"
            )

            self.console.resize(
                900,
                600
            )

        self.console.append(
            str(message)
        )

        self.console.show()

    def show_console(self):

        if hasattr(
            self,
            "console"
        ):

            self.console.show()

        else:

            self.console_message(
                "REV3 Console — Ready."
            )

    def focus_unit_selector(self):
        """Focus the display-unit selector without changing its current value."""
        if hasattr(self, "unit_combo"):
            self.unit_combo.setFocus()
            self.unit_combo.showPopup()
            self.statusBar().showMessage("Select dashboard display units: Metric or Imperial")

    def show_model_information(self):
        """Show read-only metadata obtained from the actual REV3 model."""
        d = getattr(self, "model_data", {})
        dimensions = d.get("dimensions") or []
        if self.display_units == "Imperial" and dimensions:
            dim_text = " × ".join(f"{v * M_TO_FT:.3f}" for v in dimensions) + " ft"
        elif dimensions:
            dim_text = " × ".join(f"{v:g}" for v in dimensions) + " m"
        else:
            dim_text = "Unavailable"

        dialog = QDialog(self)
        dialog.setWindowTitle("REV3 — Model Information")
        dialog.resize(520, 430)
        layout = QVBoxLayout(dialog)

        title = QLabel("REV3 MODEL INFORMATION")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText(
            f"MODEL\n"
            f"{d.get('nodes', '—')} Nodes  •  {d.get('members', '—')} Members\n"
            f"{d.get('dof', '—')} DOF\n"
            f"Dimensions: {dim_text}\n\n"
            f"MATERIAL / SECTION\n"
            f"{d.get('material') or 'Unavailable'}\n"
            f"Section: {d.get('section') or 'Unavailable'}\n\n"
            f"LOAD FRAMEWORK\n"
            f"{d.get('load_cases', '—')} Load Cases  •  {d.get('combinations', '—')} Combinations\n\n"
            f"SUPPORT CONDITIONS\n"
            f"Pinned Supports\n\n"
            f"DIAPHRAGM\n"
            f"{d.get('diaphragm') or 'Not reported'}"
        )
        layout.addWidget(info)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    def show_solver_scope(self):
        """Show the current solver scope without claiming unsupported results."""
        QMessageBox.information(
            self,
            "REV3 — Solver Scope",
            "IMPLEMENTED\n"
            "✓ Load definition\n"
            "✓ Load-case validation\n"
            "✓ Load combinations\n"
            "✓ Temperature-load framework\n"
            "✓ Visualization\n\n"
            "OUT OF SCOPE\n"
            "• Stiffness solution / displacement response\n"
            "• Support reactions\n"
            "• Member-force response\n"
            "• Drift results\n\n"
            "The dashboard reports the implemented REV3 scope and does not fabricate structural response results."
        )

    # ========================================================
    # PROJECT
    # ========================================================

    def open_project(self):

        QMessageBox.information(
            self,
            "REV3 Project",
            "Current Project:\n\n"
            + str(BASE_DIR)
        )

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):

        QMessageBox.information(
            self,
            "About REV3",
            "CUBE STRUCTURAL SOLVER — REV3\n\n"
            "PyQt6 Structural Engineering Dashboard\n\n"
            "8 Nodes • 12 Members • 48 DOF\n"
            "6.0 m Cube • ASTM A36 Steel\n\n"
            "REV3 Command Center"
        )

    # ========================================================
    # STYLE
    # ========================================================

    def apply_style(self):

        self.setStyleSheet("""
            QMainWindow {
                background: #0b1220;
                color: #e5e7eb;
            }
            QFrame#infoCard {
                background: #0f172a;
                border: 1px solid #263244;
                border-radius: 7px;
            }
            QLabel#panelTitle {
                color: #dbeafe;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }
            QLabel#cardTitle {
                color: #93c5fd;
                font-size: 10px;
                font-weight: 700;
            }
            QLabel#cardValue {
                color: #e5e7eb;
                font-size: 12px;
            }
            QLabel#selectorLabel {
                color: #94a3b8;
                font-weight: 600;
            }
            QLabel#modelDisplay {
                background: #0f172a;
                border: 1px solid #263244;
                border-radius: 8px;
                padding: 4px;
            }
            QMenuBar {
                background: #111827;
                color: #e5e7eb;
                border-bottom: 1px solid #263244;
                padding: 3px 6px;
            }
            QMenuBar::item {
                padding: 6px 10px;
                border-radius: 5px;
            }
            QMenuBar::item:selected {
                background: #1e3a5f;
            }
            QMenu {
                background: #111827;
                color: #e5e7eb;
                border: 1px solid #334155;
                padding: 5px;
            }
            QMenu::item {
                padding: 7px 24px 7px 10px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #1e3a5f;
            }
            QToolBar {
                background: #111827;
                border: none;
                border-bottom: 1px solid #263244;
                spacing: 6px;
                padding: 7px 9px;
            }
            QToolButton {
                background: #172033;
                color: #e5e7eb;
                border: 1px solid #2d3a4f;
                border-radius: 6px;
                padding: 7px 11px;
            }
            QToolButton:hover {
                background: #21304a;
                border-color: #4b6385;
            }
            QToolButton:pressed {
                background: #263d5e;
            }
            QDockWidget {
                color: #e5e7eb;
                font-weight: 700;
            }
            QDockWidget::title {
                background: #111827;
                padding: 8px;
                border-bottom: 1px solid #263244;
            }
            QGroupBox {
                background: #111827;
                border: 1px solid #263244;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                font-weight: 700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #93c5fd;
            }
            QLabel {
                color: #e5e7eb;
            }
            QTreeWidget, QListWidget {
                background: #0f172a;
                alternate-background-color: #111827;
                color: #dbe4f0;
                border: 1px solid #263244;
                border-radius: 6px;
                padding: 4px;
            }
            QTreeWidget::item, QListWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background: #1e3a5f;
                color: #ffffff;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                background: #0f172a;
                color: #e5e7eb;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 9px;
                min-height: 18px;
            }
            QComboBox::drop-down {
                border: none;
                width: 26px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {
                border-color: #4b6385;
            }
            QPushButton {
                background: #1e3a5f;
                color: #f8fafc;
                border: 1px solid #355d8c;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 20px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #28517e;
            }
            QPushButton:pressed {
                background: #173552;
            }
            QStatusBar {
                background: #111827;
                color: #94a3b8;
                border-top: 1px solid #263244;
            }
            QScrollArea {
                border: none;
            }
        """)


# ============================================================
# APPLICATION
# ============================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName(
        "CUBE Structural Solver REV3"
    )

    window = Rev3Dashboard()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
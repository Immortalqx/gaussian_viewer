# SPDX-FileCopyrightText: Copyright (c) 2021-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import os
import imgui
from gui_utils import imgui_utils


class LoadWidget:
    def __init__(self, viz, root):
        self.viz = viz
        self.root = root
        self.filter = ""
        self.items = self.list_runs_and_pkls()
        if len(self.items) == 0:
            raise FileNotFoundError(f"No .ply or compression_config.yml found in '{root}' with filter 'f{self.filter}'")
        self.ply = self.items[0]

    @imgui_utils.scoped_by_object_id
    def __call__(self, show=True):
        viz = self.viz
        if show:
            _changed, self.filter = imgui.input_text("Filter", self.filter)
            if imgui_utils.button("Browse", width=viz.button_w, enabled=True):
                imgui.open_popup("browse_pkls_popup")
                self.items = self.list_runs_and_pkls()

            if imgui.begin_popup("browse_pkls_popup"):
                for item in self.items:
                    clicked, _state = imgui.menu_item(os.path.relpath(item, self.root))
                    if clicked:
                        self.ply = item
                imgui.end_popup()

            imgui.same_line()
            imgui.text(self.ply.split("/")[-2] + " : " + self.ply.split("/")[-1].split("_")[-1].split(".")[0])

            rh_flag = self.ply.split("/")[-1].split("_")[0]
            if imgui_utils.button("Switch", width=viz.button_w, enabled=True):
                if rh_flag == "rgb":
                    rh_flag = "hot"
                    self.ply = self.ply.replace("rgb_", "hot_")
                else:
                    rh_flag = "rgb"
                    self.ply = self.ply.replace("hot_", "rgb_")
            imgui.same_line()
            imgui.text("current mode : " + rh_flag)

        viz.args.ply_file_path = self.ply
        viz.args.current_ply_name = self.ply.replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_")

    def list_runs_and_pkls(self):
        self.items = []
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file.endswith(".ply") or file.endswith("compression_config.yml") or file.endswith(".pkl"):
                    current_path = os.path.join(root, file)
                    if all([filter in current_path for filter in self.filter.split(",")]):
                        self.items.append(current_path)
        return sorted(self.items)

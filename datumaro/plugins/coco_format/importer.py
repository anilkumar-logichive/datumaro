
# Copyright (C) 2019-2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

from glob import glob
import logging as log
import os.path as osp

from datumaro.components.extractor import Importer
from datumaro.util import parse_str_enum_value
from datumaro.util.log_utils import logging_disabled

from .format import CocoTask


class CocoImporter(Importer):
    _TASKS = {
        CocoTask.instances: 'coco_instances',
        CocoTask.person_keypoints: 'coco_person_keypoints',
        CocoTask.captions: 'coco_captions',
        CocoTask.labels: 'coco_labels',
        CocoTask.image_info: 'coco_image_info',
        CocoTask.panoptic: 'coco_panoptic',
        CocoTask.stuff: 'coco_stuff',
    }

    @classmethod
    def detect(cls, path):
        with logging_disabled(log.WARN):
            return len(cls.find_sources(path)) != 0

    def __call__(self, path, **extra_params):
        from datumaro.components.project import Project  # cyclic import
        project = Project()

        subsets = self.find_sources(path)

        if len(subsets) == 0:
            raise Exception("Failed to find 'coco' dataset at '%s'" % path)

        # TODO: should be removed when proper label merging is implemented
        conflicting_types = {CocoTask.instances,
            CocoTask.person_keypoints, CocoTask.labels,
            CocoTask.panoptic, CocoTask.stuff}
        ann_types = set(t for s in subsets.values() for t in s) \
            & conflicting_types
        if 1 <= len(ann_types):
            selected_ann_type = sorted(ann_types, key=lambda x: x.name)[0]
        if 1 < len(ann_types):
            log.warning("Not implemented: "
                "Found potentially conflicting source types with labels: %s. "
                "Only one type will be used: %s" \
                % (", ".join(t.name for t in ann_types), selected_ann_type.name))

        for ann_files in subsets.values():
            for ann_type, ann_file in ann_files.items():
                if ann_type in conflicting_types:
                    if ann_type is not selected_ann_type:
                        log.warning("Not implemented: "
                            "conflicting source '%s' is skipped." % ann_file)
                        continue
                log.info("Found a dataset at '%s'" % ann_file)

                source_name = osp.splitext(osp.basename(ann_file))[0]
                project.add_source(source_name, {
                    'url': ann_file,
                    'format': self._TASKS[ann_type],
                    'options': dict(extra_params),
                })

        return project

    @classmethod
    def find_sources(cls, path):
        if path.endswith('.json') and osp.isfile(path):
            subset_paths = [path]
        else:
            subset_paths = glob(osp.join(path, '**', '*_*.json'),
                recursive=True)

        subsets = {}
        for subset_path in subset_paths:
            name_parts = osp.splitext(osp.basename(subset_path))[0] \
                .rsplit('_', maxsplit=1)

            ann_type = parse_str_enum_value(name_parts[0], CocoTask,
                default=None)
            if ann_type not in cls._TASKS:
                continue

            subset_name = name_parts[1]
            subsets.setdefault(subset_name, {})[ann_type] = subset_path

        return subsets


class CocoImageInfoImporter(CocoImporter):
    _TASK = CocoTask.image_info
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoCaptionsImporter(CocoImporter):
    _TASK = CocoTask.captions
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoInstancesImporter(CocoImporter):
    _TASK = CocoTask.instances
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoPersonKeypointsImporter(CocoImporter):
    _TASK = CocoTask.person_keypoints
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoLabelsImporter(CocoImporter):
    _TASK = CocoTask.labels
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoPanopticImporter(CocoImporter):
    _TASK = CocoTask.panoptic
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

class CocoStuffImporter(CocoImporter):
    _TASK = CocoTask.stuff
    _TASKS = { _TASK: CocoImporter._TASKS[_TASK] }

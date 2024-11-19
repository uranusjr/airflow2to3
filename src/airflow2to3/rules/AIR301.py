from __future__ import annotations

import dataclasses
import typing

import libcst as cst
from libcst.codemod.visitors import AddImportsVisitor
from libcst.metadata import MetadataWrapper, QualifiedNameProvider

if typing.TYPE_CHECKING:
    from collections.abc import Iterator

    from libcst import Module
    from libcst.codemod import CodemodContext


def _is_airflow_dag_call(qualname: str) -> bool:
    if len(components := qualname.split(".")) < 2:
        return False
    return components[0] == "airflow" and components[-1] in ("DAG", "dag")


@dataclasses.dataclass
class _ProcessDagArgs:
    node: cst.Call
    context: CodemodContext
    needs_new_arg: bool = True

    def __iter__(self) -> Iterator[cst.Arg]:
        for arg in self.node.args:
            if not arg.keyword:
                yield arg
            elif arg.keyword.value in ("timetable", "schedule_interval"):
                self.needs_new_arg = False
                yield arg.with_changes(keyword=cst.Name(value="schedule"))
            else:
                yield arg
        if self.needs_new_arg:
            AddImportsVisitor.add_needed_import(
                self.context,
                "datetime",
                "timedelta",
            )
            yield cst.Arg(
                value=cst.parse_expression("timedelta(days=1)"),
                keyword=cst.Name(value="schedule"),
                equal=cst.AssignEqual(
                    cst.SimpleWhitespace(""),
                    cst.SimpleWhitespace(""),
                ),
            )


@dataclasses.dataclass
class _DagScheduleArgumentFixer(cst.CSTTransformer):
    context: CodemodContext
    need_import: bool = False

    METADATA_DEPENDENCIES: typing.ClassVar = [QualifiedNameProvider]

    def leave_Call(
        self,
        or_node: cst.Call,
        up_node: cst.Call,
    ) -> cst.BaseExpression:
        qualname, = self.get_metadata(QualifiedNameProvider, or_node.func)
        if not _is_airflow_dag_call(qualname.name):
            return or_node
        if any(
            arg.keyword and arg.keyword.value == "schedule"
            for arg in or_node.args
        ):
            return or_node

        processor = _ProcessDagArgs(up_node, context=self.context)
        updated_args = list(processor)
        self.need_import = self.need_import or processor.needs_new_arg
        return up_node.with_changes(args=updated_args)


def fix(module: Module, context: CodemodContext) -> Module:
    fixer = _DagScheduleArgumentFixer(context)
    wrapper = MetadataWrapper(module)
    updated = wrapper.visit(fixer)
    if fixer.need_import:
        updated = AddImportsVisitor(context).transform_module(updated)
    return updated

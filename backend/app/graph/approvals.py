from app.graph.graph_builder import compiled_graph


def list_pending_approvals() -> list[dict]:
    """Unchanged from Step 12.3."""
    seen_thread_ids = set()

    checkpointer = compiled_graph.checkpointer
    for checkpoint_tuple in checkpointer.list(None):
        thread_id = checkpoint_tuple.config["configurable"]["thread_id"]
        seen_thread_ids.add(thread_id)

    pending = []
    for thread_id in seen_thread_ids:
        config = {"configurable": {"thread_id": thread_id}}
        state = compiled_graph.get_state(config)

        if state.next:
            for task in state.tasks:
                if task.interrupts:
                    for intr in task.interrupts:
                        pending.append({
                            "thread_id": thread_id,
                            "payload": intr.value,
                        })

    return pending


class ThreadNotPendingError(Exception):
    """Raised when attempting to resume a thread that isn't actually paused."""
    pass


def resume_approval(thread_id: str, approved: bool, note: str = "") -> dict:
    """
    Resumes a paused thread with a human decision. Now verifies the thread
    is genuinely paused (has a real pending interrupt) BEFORE calling
    Command(resume=...) — prevents double-resuming an already-resolved
    thread, or resuming a thread that was never paused in the first place.
    """
    from langgraph.types import Command

    config = {"configurable": {"thread_id": thread_id}}
    state = compiled_graph.get_state(config)

    if not state.next:
        raise ThreadNotPendingError(
            f"Thread '{thread_id}' is not currently awaiting approval "
            "(it may have already been resolved, or never existed)."
        )

    has_interrupt = any(task.interrupts for task in state.tasks)
    if not has_interrupt:
        raise ThreadNotPendingError(
            f"Thread '{thread_id}' is not paused on an approval interrupt."
        )

    result = compiled_graph.invoke(
        Command(resume={"approved": approved, "note": note}),
        config=config,
    )
    return result
import asyncio
import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from opentelemetry import trace

from base import app


logger = logging.getLogger("otel-datadog-tests.worker")
tracer = trace.get_tracer("otel-datadog-tests.nagger")


@app.task(bind=True)
def check(self):
    logger.info("Bound headers: %s", self.request.headers)
    with tracer.start_as_current_span("checking") as span:
        context = span.get_span_context()
        return {
            "worker_trace_id": context.trace_id,
            "worker_span_id": context.span_id,
        }


@app.task
def chat(question: str) -> str:
    model = ChatOpenAI(model="gpt-4")
    message = HumanMessage(content=question)
    response: AIMessage = asyncio.run(model.ainvoke([message]))

    return response.content

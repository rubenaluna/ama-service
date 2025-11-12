import logging
from ariadne import gql, make_executable_schema, SubscriptionType
from src.inference.inference import infer

logger = logging.getLogger(__name__)

subscription = SubscriptionType()


@subscription.source("ask")
async def ask_source(_, info, question: str):
    response = await infer(question)

    answer = ""
    async for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            answer += delta
            yield delta

    logger.info(f"\n\tQuestion: {question} \n\tAnswer: {answer}")
    yield ""


@subscription.field("ask")
async def ask_field(event, info, question: str):
    return event


schema = make_executable_schema(
    gql(
        """
  type Query {
    ask(question: String!): String!
  }
  type Subscription {
    ask(question: String!): String!
  }
"""
    ),
    subscription,
)

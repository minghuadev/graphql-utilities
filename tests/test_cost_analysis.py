from typing import List
from unittest.mock import Mock

from graphql import graphql_sync, TypeInfo, GraphQLError, visit, ValidationContext, parse

from graphql_utilities import ExtendedExecutionContext
from graphql_utilities.validate import ValidationAbortedError
from graphql_utilities.visitor import CostAnalysisVisitor
from tests.helpers import assert_no_errors, assert_has_data
from tests.resolver import PostRootResolver
from tests.schema import post_schema


def describe_cost_analysis():
    resolver = PostRootResolver()
    on_error_stub = Mock()

    def get_posts_query(first=10):
        return """
            query {
                posts(first: """ + str(first) + """) {
                    postId
                }
            }
        """

    def get_single_post_query():
        return """
            query getPostXXX {
                post(id: "XXXXXXXXXXXXXX") {
                    postId
                    title
                    author {
                        name
                    }
                }
            }
        """

    def test_schema_get_posts():
        result = graphql_sync(post_schema, get_posts_query(5), resolver)
        posts = result.data.get("posts")
        assert_no_errors(result)
        assert len(posts) == 5

    def test_schema_get_single_post():
        result = graphql_sync(post_schema, get_single_post_query(), resolver)
        assert_no_errors(result)
        assert_has_data(result)

    def calculate_cost(ast_document, max_complexity=100) -> int:
        context = ValidationContext(schema=post_schema, ast=ast_document,
                                    type_info=TypeInfo(post_schema), on_error=on_error_stub)
        visitor = CostAnalysisVisitor(context=context, max_complexity=max_complexity)
        visit(ast_document, visitor)
        return visitor.total_complexity

    def test_simple_cost():
        document = parse("""
            query getPostXXX {
                post(id: "XXXXXXXXXXXXXX") {
                    postId
                    title
                    author {
                        name
                    }
                }
            }
        """)
        complexity = calculate_cost(ast_document=document)
        assert complexity == 20

    def test_overriden_and_inherited_cost():
        document = parse("""
            query getPostXXX {
                post(id: "XXXXXXXXXXXXXX") {
                    postId
                    createdAt
                    updatedAt
                }
            }
        """)
        complexity = calculate_cost(ast_document=document)
        assert complexity == 18

    def test_multiplier():
        document = parse("""
            query {
                posts(first: 5) {
                    title
                    isPublic
                }
            }
        """)

        complexity = calculate_cost(ast_document=document)
        assert complexity == 50

    def test_multiplier_with_complexity_overriden():
        document = parse("""
                    query {
                        posts(first: 5) {
                            title
                            isPublic
                        }
                    }
                """)

        complexity = calculate_cost(ast_document=document)
        assert complexity == 20

    def test_inline_fragment():
        pass

    def test_fragment_spread():
        pass

    def test_union():
        pass
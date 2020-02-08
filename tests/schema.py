from graphql import GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString, GraphQLInt, build_schema

schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'field_1_str': GraphQLField(
                GraphQLString,
                resolve=lambda obj, info: 'str_1_field'),
            'field_2_int': GraphQLField(
                GraphQLInt,
                resolve=lambda obj, info: 2),
            'field_3_obj': GraphQLField(
                GraphQLObjectType(
                    name='Field3Object',
                    fields={
                        'field_3_obj_sub_1': GraphQLField(GraphQLObjectType(
                            name='Field3ObjectSubfield1',
                            fields={
                                'xxx': GraphQLField(GraphQLString)
                            }
                        ))
                    }
                ),
                resolve=lambda obj, info: {'field_3_obj': {'field_3_obj_sub_1': '1_sub_obj_3_field'}}
            ),
            'cat': GraphQLField(
                GraphQLObjectType(
                    name='CatObject',
                    fields={
                        'meow': GraphQLField(GraphQLString)
                    },
                ),
                resolve=lambda obj, info: {"meow": "woem"}
            )
        }))

post_schema = build_schema("""
    directive @cost(
        complexity: String
    ) on FIELD_DEFINITION 

    type Author {
        uid: String!
        name: String
        email: String
    }
    
    interface TimestampedType {
        createdAt: String
        updatedAt: String
    }
    
    type Post implements TimestampedType {
        author: Author
        postId: String!
        title: String
        text: String
        publishedAt: String
        isPublic: Boolean
        createdAt: String
        updatedAt: String
    }
    
    input PostInput {
        isPublic: Boolean = true
        isPublished: Boolean = true
    }
    
    type Query {
        posts(input: PostInput): [Post]
    }
""")

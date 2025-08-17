#!/usr/bin/env python3
"""
Simple test to verify CDK functionality
"""

from aws_cdk import App, Stack
from constructs import Construct

class TestStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

def main():
    app = App()
    TestStack(app, "test-stack")
    app.synth()

if __name__ == '__main__':
    main()

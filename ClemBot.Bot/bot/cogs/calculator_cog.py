import logging
import re

import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors
from bot.errors import ParserError

log = logging.getLogger(__name__)


class CalculatorCog(commands.Cog):

    def __init__(self, bot):
        self.operators = [
            {'symbol': "+", 'precedence': 0, 'assoc': "L"},
            {'symbol': "-", 'precedence': 0, 'assoc': "L"},
            {'symbol': "*", 'precedence': 1, 'assoc': "L"},
            {'symbol': "/", 'precedence': 1, 'assoc': "L"},
            {'symbol': "^", 'precedence': 2, 'assoc': "R"},
        ]

    @ext.command()
    @ext.long_help(
        'Native calculator in discord to evaluate any arbitrary mathematical expressions'
    )
    @ext.short_help('Does your math for you')
    @ext.example(('calc 1+1', 'calc 10/20'))
    async def calc(self, ctx, *args):
        """
        A simple calculator that supports pemdas.
        Examples:
            $calc 3(5+4)
            $calc -4*-3^5
            $calc (-10-4)/5
        """

        expression = " ".join(args)
        # issue parsing ,'s. Better to remove them
        expression = expression.replace(',', '')
        try:

            embed = discord.Embed(title="🧮Calculator", color=Colors.ClemsonOrange)

            result = self.parse_postfix(self.parse_expression(expression))

            embed.add_field(name="Expression", value=expression, inline=True)

            embed.add_field(name="Result", value=result, inline=False)

        except ParserError as error:
            embed = discord.Embed(title="🧮Calculator", color=Colors.Error)

            embed.add_field(name="Error", value=error)

        await ctx.send(embed=embed)

    # compares the precedence of two operators
    def compare_precedence(self, operator1, operator2):

        op1 = self.search_operators_symbol(operator1)

        op2 = self.search_operators_symbol(operator2)

        return op1['precedence'] <= op2['precedence']

    # searches through a list operators and return its information
    def search_operators_symbol(self, symbol):
        for operator in self.operators:
            if symbol == operator['symbol']:
                return operator

    # checks if symbol is an operator
    def is_operator(self, symbol):
        for op in self.operators:
            if symbol == op['symbol']:
                return True
        return False

    # returns the last element in a list
    def get_top_stack(self, stack):
        return stack[len(stack) - 1]

    def isNum(self, token):
        try:
            float(token)
        except ValueError:
            return False
        return True

    def isOp(self, token):
        ops = ["+", "-", "*", "/", "^", "(", ")"]
        if token in ops:
            return True
        else:
            return False

    def validateExpression(self, expression):
        numbers = 0
        operators = 0

        for token in expression:
            if self.is_operator(token):
                operators += 1
            elif self.isNum(token):
                numbers += 1

        if numbers <= operators:
            return False
        return True

    def preprocess(self, expression):
        processed = ""
        index = 0
        while index < len(expression) - 1:

            currentToken = expression[index]
            nextToken = expression[index + 1]

            if self.isOp(currentToken) and self.isOp(nextToken):
                # checks for implicit multiplication ex. (4+5)(60-5)
                if currentToken == ")" and nextToken == "(":
                    processed += f"{currentToken} * "
                    index += 1
                # Checks for implicit negative conversions
                elif currentToken == "-" and (index == 0 or (self.isOp(expression[index - 1]) and expression[index - 1] != ")")):
                    processed += "-1 * "
                    index += 1
                else:
                    processed += f"{currentToken} "
                    index += 1

            elif self.isNum(currentToken) and self.isOp(nextToken):
                # checks for implicit multiplication ex. 2(4+5)
                if nextToken == "(":
                    processed += f"{currentToken} * "
                    index += 1
                else:
                    processed += f"{currentToken} "
                    index += 1
            elif self.isOp(currentToken) and self.isNum(nextToken):
                # Determines whether or not - means subtraction or a negative number
                if currentToken == "-" and index - 1 >= 0:
                    if expression[index - 1] == ")" or self.isNum(expression[index - 1]):
                        processed += f"{currentToken} "
                        index += 1
                    else:
                        processed += f"{currentToken}"
                        index += 1
                elif currentToken == ")" and self.isNum(nextToken):
                    processed += f"{currentToken} * "
                    index += 1
                else:
                    processed += f"{currentToken}"
                    index += 1

            else:
                processed += f"{currentToken}"
                index += 1

        # adds the last token
        processed += f"{expression[len(expression) - 1]}"

        return processed

    def parse_expression(self, expression):

        expression = self.preprocess(expression)

        # parse expression into a list of numbers and symbols
        tokens = re.findall(r"-?\d*\.?\d*|[+^/*()-]", expression)

        if self.validateExpression(tokens) is False:
            raise ParserError(f"Equation not properly balanced")
        output_queue = []

        operator_stack = []

        for token in tokens:

            intFlag = 1
            try:
                float(token)
            except ValueError:
                intFlag = 0

            if intFlag:
                output_queue.append(token)

            elif token == "(":
                operator_stack.append(token)

            elif token == ")":
                # Ensures that proper precedence is followed with parentheses
                while self.get_top_stack(operator_stack) != '(':
                    output_queue.append(self.get_top_stack(operator_stack))
                    operator_stack.pop()
                operator_stack.pop()

            elif self.is_operator(token):
                # Makes sure precedence is followed for operators
                while (len(operator_stack) != 0 and (self.get_top_stack(operator_stack) not in "()")
                       and self.compare_precedence(token, self.get_top_stack(operator_stack))
                       and self.search_operators_symbol(token)['assoc'] == "L"):
                    output_queue.append(self.get_top_stack(operator_stack))
                    operator_stack.pop()
                operator_stack.append(token)

        while len(operator_stack) != 0:
            output_queue.append(self.get_top_stack(operator_stack))
            operator_stack.pop()

        return output_queue

    def calculate(self, num1, num2, sign):

        if sign == "+":
            result = num1 + num2
        elif sign == "-":
            result = num1 - num2
        elif sign == "*":
            result = num1 * num2
        elif sign == "^":
            result = num1 ** num2
        else:
            result = num1 / num2

        return result

    def parse_postfix(self, expression):

        # stores numbers to calculated
        num_stack = []

        result = 0

        for token in expression:

            intFlag = 1
            try:
                float(token)
            except ValueError:
                intFlag = 0

            if intFlag:
                num_stack.append(float(token))

            else:
                # performs a calculation using the top two numbers on the number stack
                num1 = num_stack[len(num_stack) - 2]

                num2 = num_stack[len(num_stack) - 1]

                sign = token

                result = self.calculate(num1, num2, sign)

                # removes the top two numbers and adds the result
                num_stack.pop()
                num_stack.pop()
                num_stack.append(result)

        return result


def setup(bot):
    bot.add_cog(CalculatorCog(bot))

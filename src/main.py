import asyncio
from src.cli import parse_args
from src.agent_runner import run_contract

async def main():
    args = parse_args()
    try:
        result_message = await run_contract(vars(args))
        print(result_message)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

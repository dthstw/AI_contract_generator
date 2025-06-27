import os
from tools.document_reader import read_contract_file
from agents import Agent, Runner, RunConfig, ModelSettings
from core.model_provider import OpenAIModelProvider

def create_contract_review_agent() -> Agent:
    """
    Creates and configures an AI agent specifically for contract review.
    
    Returns:
        Agent: An instance of the configured contract review Agent.
    """
    return Agent(
        name="Contract Review Agent",
        instructions="""You are a Japanese legal expert specializing in contract review and analysis.
        
Your role is to:
1. Read and analyze Japanese business contracts
2. Identify legal risks and potential issues
3. Provide detailed review reports with improvement suggestions
4. Ensure contracts comply with Japanese business law
5. Offer practical recommendations for contract optimization

You have access to document reading tools to analyze contract files.
Always provide comprehensive, professional analysis in Japanese.

Use the `read_contract_file` tool to read contract files from disk.
Provide detailed analysis covering legal risks, contract terms, and improvement suggestions.""",
        tools=[read_contract_file]
    )

class ContractReviewAgent:
    """
    Contract Review Agent for analyzing Japanese business contracts.
    This agent specializes in reviewing contracts, identifying risks,
    and providing improvement suggestions.
    """
    
    def __init__(self):
        """Initialize the Contract Review Agent."""
        self.agent = create_contract_review_agent()
    
    async def review_contract(self, contract_file_path: str, review_type: str = "comprehensive") -> str:
        """
        Review a contract file and provide detailed analysis.
        
        Args:
            contract_file_path (str): Path to the contract file to review
            review_type (str): Type of review ("comprehensive", "summary", "risk_analysis")
            
        Returns:
            str: Detailed contract review analysis
        """
        
        try:
            # Create the review instruction
            review_instruction = f"""
Please read the contract file at: {contract_file_path}

After reading the file, analyze the contract content and provide a {review_type} review.

Follow these steps:
1. Use the read_contract_file tool to read the contract
2. Analyze the contract content thoroughly
3. Provide a detailed review based on the contract content

Focus on Japanese business law compliance and practical recommendations.
Present your analysis in professional Japanese format.
"""
            
            # Configure the runner
            run_config = RunConfig(
                model_provider=OpenAIModelProvider(),
                model_settings=ModelSettings(
                    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
                    max_tokens=4000,
                ),            
            )
            
            # Run the agent
            result = await Runner.run(
                self.agent,
                input=review_instruction,
                run_config=run_config,
            )
            
            return result.final_output
            
        except Exception as e:
            return f"Error during contract review: {str(e)}" 
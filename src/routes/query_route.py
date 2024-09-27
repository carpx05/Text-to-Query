from flask import Blueprint, request, jsonify
import os
import sys
import logging

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_dir)
from src.agents.orchestrator_agent import OrchestratorAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

query_bp = Blueprint('query_route', __name__)
orchestrator = OrchestratorAgent()

@query_bp.route('/query', methods=['POST'])
def process_query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400

    query = data['query']
    try:
        print(f"Processing query: {query}")
        result, query_type, sources = orchestrator.orchestrate_query(query)
        # return jsonify(result), 200
        return jsonify({'result': result, 'query_type': query_type, 'sources': sources}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@query_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200
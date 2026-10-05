import base64
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database
ORDERS = [
    {"id": 1, "status": "paid", "customer_id": "c1", "total": 100},
    {"id": 2, "status": "pending", "customer_id": "c2", "total": 50},
    {"id": 3, "status": "paid", "customer_id": "c1", "total": 200},
    {"id": 4, "status": "shipped", "customer_id": "c3", "total": 150},
    {"id": 5, "status": "paid", "customer_id": "c4", "total": 300},
    {"id": 6, "status": "pending", "customer_id": "c1", "total": 120},
    {"id": 7, "status": "paid", "customer_id": "c2", "total": 80},
    {"id": 8, "status": "shipped", "customer_id": "c1", "total": 90},
    {"id": 9, "status": "paid", "customer_id": "c5", "total": 400},
    {"id": 10, "status": "cancelled", "customer_id": "c2", "total": 10},
]

def encode_cursor(item_id):
    cursor_data = json.dumps({"id": item_id})
    return base64.b64encode(cursor_data.encode('utf-8')).decode('utf-8')

def decode_cursor(cursor):
    try:
        cursor_bytes = base64.b64decode(cursor)
        cursor_data = json.loads(cursor_bytes.decode('utf-8'))
        return cursor_data.get('id')
    except Exception:
        return None

@app.route('/orders', methods=['GET'])
def get_orders():
    # 2. Filter: status, customer_id
    status_filter = request.args.get('status')
    customer_id_filter = request.args.get('customer_id')
    
    filtered_orders = ORDERS
    if status_filter:
        filtered_orders = [o for o in filtered_orders if o['status'] == status_filter]
    if customer_id_filter:
        filtered_orders = [o for o in filtered_orders if o['customer_id'] == customer_id_filter]
        
    # 3. Sort: sort
    sort_param = request.args.get('sort', 'id')
    descending = False
    if sort_param.startswith('-'):
        descending = True
        sort_param = sort_param[1:]
        
    if sort_param not in ['id', 'total', 'status', 'customer_id']:
        sort_param = 'id'
        
    filtered_orders.sort(key=lambda x: x[sort_param], reverse=descending)
    
    # 1. Cursor Pagination
    try:
        limit = int(request.args.get('limit', 10))
    except ValueError:
        limit = 10
        
    cursor = request.args.get('cursor')
    
    start_index = 0
    if cursor:
        cursor_id = decode_cursor(cursor)
        if cursor_id is None:
            return jsonify({"error": "Invalid cursor format"}), 400
        
        found_idx = -1
        for i, o in enumerate(filtered_orders):
            if str(o['id']) == str(cursor_id):
                found_idx = i
                break
        
        if found_idx == -1:
            return jsonify({"error": "Cursor item not found"}), 400
            
        start_index = found_idx + 1

    paginated_orders = filtered_orders[start_index : start_index + limit]
    
    # Next cursor
    next_cursor = None
    if start_index + limit < len(filtered_orders):
        last_item = paginated_orders[-1]
        next_cursor = encode_cursor(last_item["id"])

    # 4. Sparse Fieldsets
    fields_param = request.args.get('fields')
    if fields_param:
        fields = [f.strip() for f in fields_param.split(',')]
        result_orders = []
        for o in paginated_orders:
            filtered_o = {k: v for k, v in o.items() if k in fields}
            result_orders.append(filtered_o)
    else:
        result_orders = paginated_orders

    return jsonify({
        "data": result_orders,
        "pagination": {
            "next_cursor": next_cursor,
            "limit": limit
        }
    }), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)

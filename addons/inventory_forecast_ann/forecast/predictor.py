import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import MinMaxScaler

def predict_inventory(product_id, env):
    stock_move = env['stock.move']
    warehouse_id = 19  # ⚠️ Cập nhật theo ID kho nội bộ của bạn

    # Lấy lịch sử dịch chuyển sản phẩm
    moves = stock_move.search_read([
        ('product_id', '=', product_id),
        ('state', '=', 'done'),
    ], ['product_uom_qty', 'date', 'location_id', 'location_dest_id'])

    df = pd.DataFrame(moves)
    if df.empty:
        return 0

    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)

    def classify(row):
        if row['location_dest_id'][0] == warehouse_id:
            return 'in'
        elif row['location_id'][0] == warehouse_id:
            return 'out'
        return 'other'

    df['type'] = df.apply(classify, axis=1)
    df = df[df['type'].isin(['in', 'out'])]

    grouped = df.groupby(['week', 'type'])['product_uom_qty'].sum().unstack(fill_value=0).reset_index()
    grouped = grouped.sort_values(by='week')

    if len(grouped) < 4:
        return 0

    # Huấn luyện mô hình
    X, y = [], []
    for i in range(2, len(grouped) - 1):
        x = [
            grouped.iloc[i-2]['in'], grouped.iloc[i-2]['out'],
            grouped.iloc[i-1]['in'], grouped.iloc[i-1]['out'],
        ]
        y_val = grouped.iloc[i]['in'] - grouped.iloc[i]['out']
        X.append(x)
        y.append(y_val)

    X, y = np.array(X), np.array(y)

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    y_scaled = y / (y.max() if y.max() > 0 else 1)

    model = Sequential([
        Dense(8, activation='relu', input_shape=(4,)),
        Dense(4, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_scaled, y_scaled, epochs=30, batch_size=8, verbose=0)

    x_pred = [
        grouped.iloc[-2]['in'], grouped.iloc[-2]['out'],
        grouped.iloc[-1]['in'], grouped.iloc[-1]['out'],
    ]
    x_pred_scaled = scaler.transform([x_pred])
    y_pred_scaled = model.predict(x_pred_scaled, verbose=0)
    y_pred = y_pred_scaled[0][0] * y.max()

    return max(0, float(y_pred))

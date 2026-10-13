
import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(
    page_title="AI Trading Platform",
    page_icon="📈",
    layout="wide"
)

if "cash" not in st.session_state:
    st.session_state.cash = 10000.0
if "positions" not in st.session_state:
    st.session_state.positions = {}
if "trades" not in st.session_state:
    st.session_state.trades = []
if "prices" not in st.session_state:
    st.session_state.prices = {
        "AAPL": 230.0,
        "NVDA": 180.0,
        "TSLA": 440.0,
        "MSFT": 510.0,
        "AMZN": 225.0,
        "GOOGL": 245.0,
        "XAU/USD": 4200.0
    }

st.title("🤖 AI Multi-Asset Trading")
st.caption("Paper Trading Only · No Real Money")

st.warning(
    "Demo mode: prices are simulated, not live market data. "
    "Do not use these prices for real trading."
)

with st.sidebar:
    st.header("⚙️ Settings")
    auto_trade = st.toggle("Enable Auto Trading", value=False)
    risk = st.slider("Risk per trade (%)", 1, 5, 2)
    st.write("Starting balance: $10,000")
    st.write("Markets: US Stocks & Gold")

st.subheader("💰 Account Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Available Cash", f"${st.session_state.cash:,.2f}")
c2.metric("Open Positions", len(st.session_state.positions))
c3.metric("Closed Trades", len(st.session_state.trades))

st.subheader("📊 Market Watch")

market = []
for symbol, price in st.session_state.prices.items():
    market.append({
        "Asset": symbol,
        "Price (Demo)": round(price, 2)
    })

st.dataframe(pd.DataFrame(market), use_container_width=True)

st.subheader("🛒 Manual Paper Trade")
asset = st.selectbox("Choose asset", list(st.session_state.prices))
side = st.radio("Action", ["Buy", "Sell"], horizontal=True)
quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.1)

price = st.session_state.prices[asset]
st.write(f"Estimated demo value: ${price * quantity:,.2f}")

if st.button("Execute Paper Trade"):
    if side == "Buy":
        cost = price * quantity
        if cost <= st.session_state.cash:
            st.session_state.cash -= cost
            if asset in st.session_state.positions:
                old = st.session_state.positions[asset]
                old_qty = old["quantity"]
                total_qty = old_qty + quantity
                old["average"] = (
                    old["average"] * old_qty + price * quantity
                ) / total_qty
                old["quantity"] = total_qty
            else:
                st.session_state.positions[asset] = {
                    "quantity": quantity,
                    "average": price,
                    "stop": price * 0.97,
                    "target": price * 1.06
                }
            st.session_state.trades.append({
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Asset": asset,
                "Action": "BUY",
                "Price": price,
                "Quantity": quantity,
                "Reason": "Manual demo order"
            })
            st.success("Demo buy completed.")
        else:
            st.error("Insufficient virtual cash.")
    else:
        position = st.session_state.positions.get(asset)
        if position and position["quantity"] >= quantity:
            st.session_state.cash += price * quantity
            position["quantity"] -= quantity
            st.session_state.trades.append({
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Asset": asset,
                "Action": "SELL",
                "Price": price,
                "Quantity": quantity,
                "Reason": "Manual demo order"
            })
            if position["quantity"] < 0.000001:
                del st.session_state.positions[asset]
            st.success("Demo sell completed.")
        else:
            st.error("No sufficient position to sell.")

st.subheader("📂 Open Positions")
if st.session_state.positions:
    rows = []
    for symbol, p in st.session_state.positions.items():
        current = st.session_state.prices[symbol]
        pnl = (current - p["average"]) * p["quantity"]
        rows.append({
            "Asset": symbol,
            "Quantity": round(p["quantity"], 4),
            "Average Entry": round(p["average"], 2),
            "Current Demo Price": round(current, 2),
            "Unrealized P/L": round(pnl, 2),
            "Stop Loss": round(p["stop"], 2),
            "Take Profit": round(p["target"], 2)
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.info("No open positions yet.")

st.subheader("🧾 Trade History")
if st.session_state.trades:
    st.dataframe(
        pd.DataFrame(st.session_state.trades[::-1]),
        use_container_width=True
    )
else:
    st.info("No trades recorded yet.")

st.caption(
    "Prototype only. Prices are random demo starting values, "
    "not live quotes. Auto trading and automatic stop-loss execution "
    "are not implemented in this version."
          )

import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# Explore SnifferBuddy data\nThe goal of this notebook is to demonstrate how the collected SnifferBuddy data can be explored using a marimo notebook.\n\nData from SnifferBuddy readings are stored in a DuckDB database on the Raspberry pi.  The location is given in the `config.py` file.  By default the location is `/home/pi/snifferbuddy/sniffer_date.duckdb.""")
    return


@app.cell
def _():
    # Get the imports
    import marimo as mo
    import altair as alt
    import duckdb
    return alt, duckdb, mo


@app.cell
def _(duckdb):
    #Build a dataframe out of all the values in the DuckDB database of SnifferBuddy readings.
    with duckdb.connect('examples\sniffer_data.duckdb') as conn:
        df = conn.execute(f"SELECT * FROM readings").df()
        print(df.tail(2))
    return conn, df


@app.cell(hide_code=True)
def _(mo):
    def show_stats(df):
        try:
            temp_avg = df['temperature'].mean()
            humid_avg = df['humidity'].mean()
            vpd_avg = df['vpd'].mean()
            co2_avg = df['CO2'].mean()

            grid = mo.hstack([
                mo.stat(
                    label="Selected", 
                    value=f"{len(df)}", 
                    bordered=True
                ),
                mo.stat(
                    label=f"{df['timestamp'].min().strftime('%Y-%m-%d')}", 
                    value=f" {df['timestamp'].min().strftime('%H:%M:%S')}", 
                    bordered=True
                ),
                mo.stat(
                    label=f"{df['timestamp'].max().strftime('%Y-%m-%d')}", 
                    value=f"{df['timestamp'].max().strftime('%H:%M:%S')}", 
                    bordered=True
                ),
                mo.stat(label="Temperature", value=f"{temp_avg:.1f}°C", bordered=True),
                mo.stat(label="Humidity", value=f"{humid_avg:.1f}%", bordered=True),
                mo.stat(label="VPD", value=f"{vpd_avg:.2f} kPa", bordered=True),
                mo.stat(label="CO₂", value=f"{co2_avg:.0f} ppm", bordered=True),
            ], justify="start")
            output = grid
        except:
            output = mo.md('#Choose a slice of the plot.')
        return output
    return (show_stats,)


@app.cell(hide_code=True)
def _(alt, mo):
    def plot_values(df):
        humidity_color = "green" #"#8ecae6"
        temperature_color = "blue" #'#0a9396'
        vpd_color = "#219ebc"
        co2_color = "#ffb703"
        # Base chart with common x-axis
        base = alt.Chart(df).encode(
            x='timestamp:T'
        ).properties(
            width=600,
            height=200
        )

        left = alt.layer(
            base.mark_line(color=temperature_color).encode(
                y=alt.Y('temperature:Q', 
                        scale=alt.Scale(domain=[20, 100]),
                        axis=alt.Axis(title='Temperature (°F) / Humidity (%)')),
                tooltip=[
                    alt.Tooltip('timestamp:T', title='Time', format='%Y-%m-%d %H:%M:%S'),
                    alt.Tooltip('temperature:Q', title='Temperature', format='.1f')
                ]
            ),
            base.mark_line(color=humidity_color).encode(
                y=alt.Y('humidity:Q', scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip('timestamp:T', title='Time', format='%Y-%m-%d %H:%M:%S'),
                    alt.Tooltip('humidity:Q', title='Humidity', format='.1f')
                ]
            )
        )

        # Right axis for VPD
        right = base.mark_line(color=vpd_color).encode(
            y=alt.Y('vpd:Q', 
                    axis=alt.Axis(
                        values=[0, 0.5, 1.0, 1.5, 2.0],  # Explicit tick values
                        format='.1f'  # One decimal place
                    ),

                    title='VPD (kPa)'),
            tooltip=[
                alt.Tooltip('timestamp:T', title='Time', format='%Y-%m-%d %H:%M:%S'),
                alt.Tooltip('vpd:Q', title='VPD', format='.2f')
            ]

        )

        # Combine with proper scale resolution
        brush = alt.selection_interval()
        _chart = alt.layer(left, right).resolve_scale(
            y='independent'
        ).add_params(brush)

        return mo.ui.altair_chart(_chart)
    return (plot_values,)


@app.cell(hide_code=True)
def _(df, plot_values):
    plot = plot_values(df)
    plot
    return (plot,)


@app.cell(hide_code=True)
def _(df, plot, show_stats):
    if plot.value.empty:
        stat_output = show_stats(df)
    else:
        stat_output = show_stats(plot.value)
    stat_output
    return (stat_output,)


@app.cell
def _(plot, plot_values):
    plot_slice = plot_values(plot.value)
    plot_slice
    return (plot_slice,)


@app.cell(hide_code=True)
def _(df, mo):
    # Let's look at light on vs light off vpd and temperature...
    temp_on = df[df['light_on'] == True]['temperature'].mean()
    temp_off = df[df['light_on'] == False]['temperature'].mean()
    vpd_on = df[df['light_on'] == True]['vpd'].mean()
    vpd_off = df[df['light_on'] == False]['vpd'].mean()

    grid = mo.hstack([
        mo.stat(
            label="Temperature", 
            value=f"{temp_on:.1f}",
            caption="Light ON",
            bordered=True
        ),
        mo.stat(
            label="Temperature", 
            value=f"{temp_off:.1f}",
            caption="Light OFF",
            bordered=True
        ),
                    mo.stat(
            label="vpd", 
            value=f"{vpd_on:.1f}",
            caption="Light ON",
            bordered=True
        ),
        mo.stat(
            label="vpd", 
            value=f"{vpd_off:.1f}",
            caption="Light OFF",
            bordered=True
        )
    ], justify="center")
    mo.vstack([
        mo.md("# Average vpd and temperature - Light ON/OFF"),
        grid
    ])
    return grid, temp_off, temp_on, vpd_off, vpd_on


if __name__ == "__main__":
    app.run()

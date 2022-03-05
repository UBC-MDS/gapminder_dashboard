# Reflections

## Dashboard Summary

The gapminder dashboard has been created to enable users to learn more about the socio-economic trends across the world. It has been built upon the Gapminder data set, which is a great source of information about these parameters and is updated from time-to-time. 

The dashboard provides the following charts:
-	A world map (top-left) highlights the region for which data is being analysed. Countries in the region are highlighted using colour gradient based on value of the parameter. A tooltip gives specific values for each country.
-	A bar chart (top-right) represents the top 10 countries in the selected region having the highest value for the parameter.
-	A line chart (bottom-left) plots the trend for the parameter over the selected time horizon. It includes overall average for the world, average for the selected region and value for the selected country. 
-	A bubble chart (bottom-right) compares the parameter with other parameters for the specified region, country and year.

## What works well

The dashboard covers a wide range of socio-economic parameters that can be analysed: population, national income, life expectancy, children per woman, child mortality rate, population density, co2 emission per capita, years in school for men, and years in school for women

It allows the users to drill down deeper into the historical trends and specific regions by providing multiple filters, such as region, country, and year. This allows the users to analyse the data at desired level of granularity. It also allows the user to compare changes in one parameter with respect to changes in other.

The dashboard is easy to use and interpret.

## Limitations and Improvement Areas

In terms of functionality, the dashboard needs the following enhancements
-	It needs to be more reactive to the changes in display environment. Currently, it works well for a large screen display with fixed resolution. But when we look at it on smaller screens, such as tablet or mobile, or when we use a different resolution, layout and size of charts does not get adjusted automatically. The functionality where plot area and chart area get adjusted as per the screen size and resolution needs to be incorporated.
-	It needs to provide some more customization options to the user looking to analyse the underlying data. Once such option is to include is a dropdown to select the order (ascending or descending) for the top countries. Another option is to provide a Range Slider for selecting the year(s) for analysis.
-	It needs to have more interactivity in all the plots. This includes the option to highlight sections of interest in all plots and grey out the other data points. This also includes the option to highlight country or region of interest on the world map and adding tooltip to all plots.

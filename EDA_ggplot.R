library(dplyr)
library(ggplot2)

setwd("/Users/alexpapiu/Documents/Data/Craigslist")
conn = src_sqlite(path = "housing.db")
housing = tbl(src = conn, from = "cl_housing_clean")

data = housing %>% select(-id.1) %>% collect()


data %>% 
    filter(price < 5000, price > 500) %>% 
    ggplot(aes(x = per_person, fill = area)) +
    geom_density() +
    scale_fill_brewer(palette = "Set1") +
    facet_wrap(~ area, ncol = 1)



data %>% 
    filter(price < 6000, price > 500) %>% 
    filter(num_bed== "1.0") %>% 
    ggplot(aes(x = price, fill = area)) +
    geom_density(alpha = 0.9)

data %>% 
    filter(price < 6000, price > 500) %>% 
    filter(num_bed== "1.0") %>% 
    ggplot(aes(x = price, fill = area)) +
    geom_density() +
    #geom_histogram()  + 
    scale_fill_brewer(palette = "Set1") +
    facet_wrap(~ area, ncol = 1)



data %>%   
    count(where, sort = T) %>% head(21) -> popular_ngb

data$where[!(data$where %in% popular_ngb$where)] = "other"

#some willamsburg are in manh - bad"
data$area[data$where == "williamsburg" & !(is.na(data$where))] = "newyorkbrk"

data %>% 
    filter(where != "other") %>% 
    filter(price < 5000, price > 500) %>% 
    #filter(num_bed== "1.0") %>% 
    ggplot(aes(x = per_person))  +
    geom_density(aes(fill = area)) +
    facet_wrap( ~ where, nrow = 4) +
    scale_fill_brewer(palette = "Set1")


data %>% 
    ggplot(aes(x = ))
    

#a lot of bimodal distributions.

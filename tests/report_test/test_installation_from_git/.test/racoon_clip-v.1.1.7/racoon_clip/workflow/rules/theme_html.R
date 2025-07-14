
theme_html <- function(){ 
  font <- "Arial"   #assign font family up front
  
  theme_bw() %+replace%    #replace elements we want to change
    
    theme(
      axis.title = element_text(size = 30,
                                color = "black"),
      # tick labels
      axis.text = element_text(size = 30,
                               color = "black"),
      # title 
      title = element_text(size = 30,
                           color = "black"),
      legend.title=element_blank(), 
      legend.text=element_text(size=30,
                               color = "black"),
      
      # facety titels
      strip.text = element_text(size=30)
    )
}


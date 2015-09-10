      function make_tab_active(id){
        if (id === null) {
        var url = location.pathname;
        var a_url = ""
        $(".nav-tabs li a").each(function(){
          a_url = $(this).attr('href')
          if (a_url === url){
            $(this).parent('li').addClass('active')
          }
        });
        }
        else {
          $("#"+id).addClass('active')
        }
      }
      function make_side_menu_active(id){
          $("#"+id).addClass('active')
      };
      $(".cover-page").click(function(){
        $('.lightbox').show();
      });

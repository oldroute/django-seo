

var APPLY_TEXTS = 1,
    GENERATE_TEXTS = 2,
    ClEAR_TEXTS = 3;

$(document).ready(function(){

    $(".tablesorter").tablesorter();

    var modal_text = 'Вы действительно хотите удалить все тексты заполненные вручную?' +
                    '<br><strong>Вернуть их отображение будет невозможно</strong>';
    $('body').append('<div id="seogen_modal">'+ modal_text +'</div>');
    var modal_container = $('#seogen_modal');
    modal_container.hide();

    function open_modal(input){

        modal_container.show();
        modal_container.dialog({
            modal: true,
            title: 'Удаление текстов',
            draggable: false,
            closeText: "Закрыть",
            resizable: false,
            autoOpen: false,
            width: 350,
            buttons:{
                "Подтвердить удаление":function(e){
                    $(this).dialog("close");
                    $(this).hide();
                },
                "Отменить":function(e){
                    $(this).dialog("close");
                    input.prop("checked", false);
                    $(this).hide();
                },
            },
        });

        modal_container.dialog("open");
    };

    function seogen_init(){

        $('input.operation[value='+ ClEAR_TEXTS +']').on('click', function(){
            var checked = $(this).prop("checked");
            if(checked==true){
                open_modal($(this));
            }
        });

        $('input.apply_is_cycled').prop('disabled', true);
        $('input.apply_type').prop('disabled', true);
        $('input.apply_type').prop('checked', false);

        $('input.operation[value='+ APPLY_TEXTS +']').on('click', function(){
            var checked = $(this).prop("checked"),
                parent = $(this).parents().eq(4);
            if(checked==true){
                parent.find('input.apply_type').prop('disabled', false);
                parent.find('input.apply_type').eq(0).prop('checked', true);
                parent.find('input.apply_is_cycled').eq(0).prop('disabled', false);
                parent.find('input.apply_is_cycled').eq(0).prop('checked', false);
            } else {
                parent.find('input.apply_type').prop('disabled', true);
                parent.find('input.apply_type').prop('checked', false);
                parent.find('input.apply_is_cycled').eq(0).prop('disabled', true);
                parent.find('input.apply_is_cycled').eq(0).prop('checked', false);
            };
        });
    };

    seogen_init();

    $('#seo-seotemplate-content_type-object_id-group .add-row').on('click', function(){
        seogen_init();
    });

});

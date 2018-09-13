 /* Временное интерфейсное решение */
$(function() {
    $(".tablesorter").tablesorter();

    $(document).find(".field-box.field-apply_type input, .field-box.field-apply_is_cycled input ").each(function(){
        $(this).prop("disabled", true);
        $(this).prop("checked", false);
        $(this).parent().css("opacity", "0.5");
    });

    $(".field-box.field-title_operation input").on("change", function(){
       // При выборе операции (де)акивировать элементы управления
       var value = $(this).attr("value");
       var parent = $(this).parents(".form-row").first();
       parent.find(".field-box.field-title_apply_type input, .field-box.field-title_apply_is_cycled input ").each(function(){
           $(this).prop("disabled", value == 1 ? false : true);
           $(this).prop("checked", value == false);
           $(this).parent().css("opacity", value == 1 ? "1" : "0.5");
           // если выбрано "Применить" то по умолчанию "свободным"
           if(value == 1 & $(this).attr("value") == 1){
               $(this).prop("checked", true);
           }
       });
    });

    $(".field-box.field-desc_operation input").on("change", function(){
       // При выборе операции (де)акивировать элементы управления
       var value = $(this).attr("value");
       var parent = $(this).parents(".form-row").first();
       parent.find(".field-box.field-desc_apply_type input, .field-box.field-desc_apply_is_cycled input ").each(function(){
           $(this).prop("disabled", value == 1 ? false : true);
           $(this).prop("checked", value == false);
           $(this).parent().css("opacity", value == 1 ? "1" : "0.5");
           // если выбрано "Применить" то по умолчанию "свободным"
           if(value == 1 & $(this).attr("value") == 1){
               $(this).prop("checked", true);
           }
       });
    });

    $(".field-box.field-keys_operation input").on("change", function(){
       // При выборе операции (де)акивировать элементы управления
       var value = $(this).attr("value");
       var parent = $(this).parents(".form-row").first();
       parent.find(".field-box.field-keys_apply_type input, .field-box.field-keys_apply_is_cycled input ").each(function(){
           $(this).prop("disabled", value == 1 ? false : true);
           $(this).prop("checked", value == false);
           $(this).parent().css("opacity", value == 1 ? "1" : "0.5");
           // если выбрано "Применить" то по умолчанию "свободным"
           if(value == 1 & $(this).attr("value") == 1){
               $(this).prop("checked", true);
           }
       });
    });

    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_0').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_0').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_0').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_1').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_1').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_type_1').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_is_cycled').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_is_cycled').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-title_apply_is_cycled').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_0').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_0').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_0').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_1').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_1').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_type_1').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_is_cycled').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_is_cycled').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-desc_apply_is_cycled').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_0').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_0').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_0').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_1').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_1').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_type_1').parent().css("opacity", "0.5");

    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_is_cycled').prop("disabled", true)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_is_cycled').prop("checked", false)
    $('#id_seo-seotemplate-content_type-object_id-0-keys_apply_is_cycled').parent().css("opacity", "0.5");


});
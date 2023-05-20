package handlers

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"strconv"

	"github.com/CCTVBackend/pkg/models"
	"github.com/gorilla/mux"
)

func (h handler) CreateOwner(w http.ResponseWriter, r *http.Request) {

	//Read request body
	defer r.Body.Close()
	body, err := ioutil.ReadAll(r.Body)

	if err != nil {
		log.Fatalln(err)
	}

	var owner models.Owner
	json.Unmarshal(body, &owner)

	//add to database and check if error
	result := h.DB.Create(&owner)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusCreated)
	w.Header().Add("Content-Type", "application/json")
	data, err := json.Marshal(owner)
	if err != nil {
		log.Println(err)
	}
	w.Write(data)
}

func (h handler) ReadOwner(w http.ResponseWriter, r *http.Request) {

	//Get id from URL
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var owner models.Owner
	// find owner in db
	if result := h.DB.First(&owner, id); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode(owner)
}

func (h handler) UpdateOwner(w http.ResponseWriter, r *http.Request) {
	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	//Read request body
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var owner models.Owner
	//Find owner in DB
	result := h.DB.First(&owner, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Overwrite owner data
	var newOwner models.Owner
	json.Unmarshal(body, &newOwner)
	owner = newOwner

	//make sure id doesnt change (to avoid dupes)
	owner.ID = uint64(id)

	//Push changes to DB
	h.DB.Save(&owner)

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Updated")

}
func (h handler) DeleteOwner(w http.ResponseWriter, r *http.Request) {

	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var owner models.Owner

	//Find owner in DB
	result := h.DB.First(&owner, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Delete owner in DB
	if result := h.DB.Delete(&owner); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Deleted")

}
